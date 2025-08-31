"""
FastAPI приложение для управления файлами в системе электронного журнала.
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
import os
from pathlib import Path
from typing import List, Optional
import uuid
import aiofiles
import asyncio
from datetime import datetime

from app.config import settings
from app.models.file_models import FileMetadata, FileUploadResponse, BulkUploadResponse
from app.services.file_service import FileService
from app.services.auth_service import AuthService
from app.utils.exceptions import FileNotFoundError, FileTypeNotSupportedError, FileTooLargeError

# Инициализация FastAPI приложения
app = FastAPI(
    title="Journal System - File Service",
    description="Микросервис для управления файлами в системе электронного журнала производства работ",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Сервисы
file_service = FileService()
auth_service = AuthService()


# Dependency для аутентификации
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Получение текущего пользователя из JWT токена"""
    token = credentials.credentials
    user = await auth_service.get_user_from_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return user


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "service": "file_service"
    }


@app.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    object_id: str = Form(...),
    entry_id: Optional[str] = Form(None),
    file_type: str = Form(...),
    location_lat: Optional[float] = Form(None),
    location_lon: Optional[float] = Form(None),
    current_user = Depends(get_current_user)
):
    """
    Загрузка файла
    
    - **file**: Загружаемый файл
    - **object_id**: ID объекта (проекта)
    - **entry_id**: ID записи журнала (опционально)
    - **file_type**: Тип файла (photo, document, certificate)
    - **location_lat**: Широта съемки (опционально)
    - **location_lon**: Долгота съемки (опционально)
    """
    try:
        # Валидация файла
        if file.size > settings.MAX_FILE_SIZE:
            raise FileTooLargeError(f"File size {file.size} exceeds maximum {settings.MAX_FILE_SIZE}")
        
        if not file_service.is_supported_file_type(file.filename, file_type):
            raise FileTypeNotSupportedError(f"File type not supported for {file_type}")
        
        # Сохранение файла
        file_metadata = await file_service.save_file(
            file=file,
            object_id=object_id,
            entry_id=entry_id,
            file_type=file_type,
            uploaded_by=current_user.id,
            location_lat=location_lat,
            location_lon=location_lon
        )
        
        return FileUploadResponse(
            success=True,
            data=file_metadata
        )
        
    except (FileTooLargeError, FileTypeNotSupportedError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")


@app.post("/bulk-upload", response_model=BulkUploadResponse)
async def bulk_upload_files(
    files: List[UploadFile] = File(...),
    metadata: str = Form(...),  # JSON string с метаданными для каждого файла
    current_user = Depends(get_current_user)
):
    """
    Массовая загрузка файлов
    
    - **files**: Список загружаемых файлов
    - **metadata**: JSON с метаданными для каждого файла
    """
    try:
        import json
        metadata_list = json.loads(metadata)
        
        if len(files) != len(metadata_list):
            raise HTTPException(status_code=400, detail="Files count must match metadata count")
        
        uploaded_files = []
        failed_files = []
        
        for file, file_meta in zip(files, metadata_list):
            try:
                file_metadata = await file_service.save_file(
                    file=file,
                    object_id=file_meta.get('object_id'),
                    entry_id=file_meta.get('entry_id'),
                    file_type=file_meta.get('file_type'),
                    uploaded_by=current_user.id,
                    location_lat=file_meta.get('location_lat'),
                    location_lon=file_meta.get('location_lon')
                )
                uploaded_files.append({
                    "file_id": file_metadata.file_id,
                    "original_name": file_metadata.original_name,
                    "status": "success"
                })
            except Exception as e:
                failed_files.append({
                    "original_name": file.filename,
                    "status": "error",
                    "error_message": str(e)
                })
        
        return BulkUploadResponse(
            success=True,
            data={
                "uploaded_files": uploaded_files + failed_files,
                "summary": {
                    "total": len(files),
                    "successful": len(uploaded_files),
                    "failed": len(failed_files)
                }
            }
        )
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid metadata JSON")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk upload failed: {str(e)}")


@app.get("/files/{file_id}")
async def get_file(
    file_id: str,
    download: bool = False,
    current_user = Depends(get_current_user)
):
    """
    Получение файла по ID
    
    - **file_id**: UUID файла
    - **download**: Принудительная загрузка (вместо отображения в браузере)
    """
    try:
        file_metadata = await file_service.get_file_metadata(file_id)
        if not file_metadata:
            raise FileNotFoundError(f"File {file_id} not found")
        
        # Проверка прав доступа
        if not await auth_service.has_file_access(current_user, file_metadata):
            raise HTTPException(status_code=403, detail="Access denied")
        
        file_path = Path(settings.STORAGE_PATH) / file_metadata.storage_path
        
        if not file_path.exists():
            raise FileNotFoundError(f"Physical file not found: {file_path}")
        
        if download:
            return FileResponse(
                path=file_path,
                filename=file_metadata.original_name,
                media_type='application/octet-stream'
            )
        else:
            return FileResponse(
                path=file_path,
                filename=file_metadata.original_name
            )
            
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File retrieval failed: {str(e)}")


@app.get("/files/{file_id}/metadata", response_model=FileMetadata)
async def get_file_metadata(
    file_id: str,
    current_user = Depends(get_current_user)
):
    """Получение метаданных файла"""
    try:
        file_metadata = await file_service.get_file_metadata(file_id)
        if not file_metadata:
            raise FileNotFoundError(f"File {file_id} not found")
        
        # Проверка прав доступа
        if not await auth_service.has_file_access(current_user, file_metadata):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return file_metadata
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.delete("/files/{file_id}")
async def delete_file(
    file_id: str,
    current_user = Depends(get_current_user)
):
    """Удаление файла"""
    try:
        file_metadata = await file_service.get_file_metadata(file_id)
        if not file_metadata:
            raise FileNotFoundError(f"File {file_id} not found")
        
        # Проверка прав доступа
        if not await auth_service.can_delete_file(current_user, file_metadata):
            raise HTTPException(status_code=403, detail="Access denied")
        
        success = await file_service.delete_file(file_id)
        if success:
            return {"success": True, "message": "File deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="File deletion failed")
            
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
