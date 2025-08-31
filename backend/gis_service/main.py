"""
GIS микросервис для работы с геопространственными данными
Электронный журнал производства работ - промышленное решение
"""

from fastapi import FastAPI, HTTPException, Depends, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import json
import aiofiles
import asyncio
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создание приложения FastAPI
app = FastAPI(
    title="GIS Service",
    description="Микросервис для работы с геопространственными данными",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================================================
# МОДЕЛИ ДАННЫХ
# ==========================================================================

class Coordinates(BaseModel):
    """Модель координат"""
    latitude: float = Field(..., ge=-90, le=90, description="Широта")
    longitude: float = Field(..., ge=-180, le=180, description="Долгота")
    altitude: Optional[float] = Field(None, description="Высота над уровнем моря")


class Address(BaseModel):
    """Модель адреса"""
    formatted_address: str = Field(..., description="Полный адрес")
    country: Optional[str] = Field(None, description="Страна")
    region: Optional[str] = Field(None, description="Регион")
    city: Optional[str] = Field(None, description="Город")
    district: Optional[str] = Field(None, description="Район")
    street: Optional[str] = Field(None, description="Улица")
    house_number: Optional[str] = Field(None, description="Номер дома")
    postal_code: Optional[str] = Field(None, description="Почтовый индекс")


class GeoPoint(BaseModel):
    """Модель геоточки"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    coordinates: Coordinates
    address: Optional[Address] = None
    properties: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)


class GeoPolygon(BaseModel):
    """Модель полигона"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    coordinates: List[List[Coordinates]] = Field(..., description="Координаты полигона")
    properties: Dict[str, Any] = Field(default_factory=dict)
    area_sqm: Optional[float] = Field(None, description="Площадь в квадратных метрах")
    perimeter_m: Optional[float] = Field(None, description="Периметр в метрах")
    created_at: datetime = Field(default_factory=datetime.now)


class GeoLine(BaseModel):
    """Модель линии/маршрута"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    coordinates: List[Coordinates] = Field(..., description="Координаты линии")
    properties: Dict[str, Any] = Field(default_factory=dict)
    length_m: Optional[float] = Field(None, description="Длина в метрах")
    created_at: datetime = Field(default_factory=datetime.now)


class ProjectGeoData(BaseModel):
    """Модель геоданных проекта"""
    project_id: str = Field(..., description="ID проекта")
    points: List[GeoPoint] = Field(default_factory=list)
    polygons: List[GeoPolygon] = Field(default_factory=list)
    lines: List[GeoLine] = Field(default_factory=list)
    bounds: Optional[Dict[str, float]] = Field(None, description="Границы области")
    center: Optional[Coordinates] = Field(None, description="Центр области")


class GeocodeRequest(BaseModel):
    """Модель запроса геокодирования"""
    address: str = Field(..., description="Адрес для геокодирования")
    country: Optional[str] = Field("RU", description="Код страны")
    limit: int = Field(1, ge=1, le=10, description="Максимальное количество результатов")


class GeocodeResponse(BaseModel):
    """Модель ответа геокодирования"""
    query: str = Field(..., description="Исходный запрос")
    results: List[Dict[str, Any]] = Field(..., description="Результаты геокодирования")
    total_found: int = Field(..., description="Общее количество найденных результатов")


class DistanceRequest(BaseModel):
    """Модель запроса расчета расстояния"""
    point1: Coordinates = Field(..., description="Первая точка")
    point2: Coordinates = Field(..., description="Вторая точка")
    unit: str = Field("meters", description="Единица измерения")
    
    @validator('unit')
    def validate_unit(cls, v):
        allowed_units = ['meters', 'kilometers', 'miles']
        if v not in allowed_units:
            raise ValueError(f'Unit must be one of {allowed_units}')
        return v


class AreaRequest(BaseModel):
    """Модель запроса расчета площади"""
    coordinates: List[Coordinates] = Field(..., min_items=3, description="Координаты полигона")
    unit: str = Field("sqm", description="Единица измерения")
    
    @validator('unit')
    def validate_unit(cls, v):
        allowed_units = ['sqm', 'sqkm', 'hectares']
        if v not in allowed_units:
            raise ValueError(f'Unit must be one of {allowed_units}')
        return v


# ==========================================================================
# ГЕОКОДИРОВАНИЕ
# ==========================================================================

class GeocodingService:
    """Сервис геокодирования"""
    
    def __init__(self):
        self.nominatim_url = "https://nominatim.openstreetmap.org"
        self.session = None
    
    async def geocode_address(self, address: str, country: str = "RU", limit: int = 1) -> List[Dict]:
        """Геокодирование адреса"""
        try:
            # В реальном проекте здесь будет интеграция с Nominatim или другим сервисом
            # Пока возвращаем мок-данные
            
            # Простая имитация геокодирования для Москвы
            if "москва" in address.lower() or "moscow" in address.lower():
                return [{
                    "formatted_address": f"{address}, Москва, Россия",
                    "coordinates": {
                        "latitude": 55.7558 + (hash(address) % 100) / 10000,
                        "longitude": 37.6176 + (hash(address) % 100) / 10000
                    },
                    "address_components": {
                        "country": "Россия",
                        "region": "Москва",
                        "city": "Москва",
                        "street": address
                    },
                    "accuracy": "street",
                    "confidence": 0.9
                }]
            
            # Для других адресов возвращаем примерные координаты
            return [{
                "formatted_address": f"{address}, Россия",
                "coordinates": {
                    "latitude": 55.0 + (hash(address) % 1000) / 100,
                    "longitude": 37.0 + (hash(address) % 1000) / 100
                },
                "address_components": {
                    "country": "Россия",
                    "street": address
                },
                "accuracy": "approximate",
                "confidence": 0.7
            }]
            
        except Exception as e:
            logger.error(f"Geocoding error: {e}")
            raise HTTPException(status_code=500, detail="Ошибка геокодирования")
    
    async def reverse_geocode(self, latitude: float, longitude: float) -> Dict:
        """Обратное геокодирование"""
        try:
            # Мок-данные для обратного геокодирования
            return {
                "formatted_address": f"ул. Примерная, д. {abs(int(latitude * 100)) % 100}, Москва, Россия",
                "coordinates": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "address_components": {
                    "country": "Россия",
                    "region": "Москва",
                    "city": "Москва",
                    "street": "ул. Примерная",
                    "house_number": str(abs(int(latitude * 100)) % 100)
                }
            }
            
        except Exception as e:
            logger.error(f"Reverse geocoding error: {e}")
            raise HTTPException(status_code=500, detail="Ошибка обратного геокодирования")


# ==========================================================================
# ГЕОМЕТРИЧЕСКИЕ РАСЧЕТЫ
# ==========================================================================

class GeometryService:
    """Сервис геометрических расчетов"""
    
    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Расчет расстояния по формуле гаверсинусов (в метрах)"""
        import math
        
        R = 6371000  # Радиус Земли в метрах
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    @staticmethod
    def calculate_polygon_area(coordinates: List[Coordinates]) -> float:
        """Расчет площади полигона в квадратных метрах"""
        import math
        
        if len(coordinates) < 3:
            return 0.0
        
        # Формула Шелеса для расчета площади полигона
        n = len(coordinates)
        area = 0.0
        
        for i in range(n):
            j = (i + 1) % n
            area += coordinates[i].longitude * coordinates[j].latitude
            area -= coordinates[j].longitude * coordinates[i].latitude
        
        area = abs(area) / 2.0
        
        # Преобразуем в квадратные метры (приблизительно)
        # Коэффициент зависит от широты
        avg_lat = sum(coord.latitude for coord in coordinates) / n
        lat_factor = math.cos(math.radians(avg_lat))
        
        # 1 градус ≈ 111320 метров
        area_sqm = area * (111320 ** 2) * lat_factor
        
        return abs(area_sqm)
    
    @staticmethod
    def calculate_line_length(coordinates: List[Coordinates]) -> float:
        """Расчет длины линии в метрах"""
        if len(coordinates) < 2:
            return 0.0
        
        total_length = 0.0
        for i in range(len(coordinates) - 1):
            distance = GeometryService.haversine_distance(
                coordinates[i].latitude, coordinates[i].longitude,
                coordinates[i + 1].latitude, coordinates[i + 1].longitude
            )
            total_length += distance
        
        return total_length
    
    @staticmethod
    def calculate_bounds(coordinates: List[Coordinates]) -> Dict[str, float]:
        """Расчет границ области"""
        if not coordinates:
            return {}
        
        lats = [coord.latitude for coord in coordinates]
        lons = [coord.longitude for coord in coordinates]
        
        return {
            "north": max(lats),
            "south": min(lats),
            "east": max(lons),
            "west": min(lons)
        }
    
    @staticmethod
    def calculate_center(coordinates: List[Coordinates]) -> Coordinates:
        """Расчет центра области"""
        if not coordinates:
            return Coordinates(latitude=0, longitude=0)
        
        avg_lat = sum(coord.latitude for coord in coordinates) / len(coordinates)
        avg_lon = sum(coord.longitude for coord in coordinates) / len(coordinates)
        
        return Coordinates(latitude=avg_lat, longitude=avg_lon)


# ==========================================================================
# ХРАНИЛИЩЕ ГЕОДАННЫХ
# ==========================================================================

class GeoDataStorage:
    """Хранилище геоданных проектов"""
    
    def __init__(self):
        self.data_dir = Path("gis_data")
        self.data_dir.mkdir(exist_ok=True)
        self.projects = {}
    
    async def save_project_geodata(self, project_id: str, geodata: ProjectGeoData) -> bool:
        """Сохранение геоданных проекта"""
        try:
            file_path = self.data_dir / f"{project_id}.json"
            
            # Подготавливаем данные для сериализации
            data = geodata.dict()
            data['updated_at'] = datetime.now().isoformat()
            
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(data, ensure_ascii=False, indent=2))
            
            self.projects[project_id] = geodata
            return True
            
        except Exception as e:
            logger.error(f"Error saving geodata for project {project_id}: {e}")
            return False
    
    async def load_project_geodata(self, project_id: str) -> Optional[ProjectGeoData]:
        """Загрузка геоданных проекта"""
        try:
            # Сначала проверяем кеш
            if project_id in self.projects:
                return self.projects[project_id]
            
            file_path = self.data_dir / f"{project_id}.json"
            if not file_path.exists():
                return None
            
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                data = json.loads(await f.read())
            
            geodata = ProjectGeoData(**data)
            self.projects[project_id] = geodata
            return geodata
            
        except Exception as e:
            logger.error(f"Error loading geodata for project {project_id}: {e}")
            return None
    
    async def delete_project_geodata(self, project_id: str) -> bool:
        """Удаление геоданных проекта"""
        try:
            file_path = self.data_dir / f"{project_id}.json"
            if file_path.exists():
                file_path.unlink()
            
            if project_id in self.projects:
                del self.projects[project_id]
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting geodata for project {project_id}: {e}")
            return False


# ==========================================================================
# ИНИЦИАЛИЗАЦИЯ СЕРВИСОВ
# ==========================================================================

geocoding_service = GeocodingService()
geometry_service = GeometryService()
storage = GeoDataStorage()


# ==========================================================================
# API ENDPOINTS
# ==========================================================================

@app.get("/", response_model=Dict[str, str])
async def root():
    """Корневой endpoint"""
    return {
        "service": "GIS Service",
        "version": "1.0.0",
        "status": "running",
        "description": "Микросервис для работы с геопространственными данными"
    }


@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/geocode", response_model=GeocodeResponse)
async def geocode_address(request: GeocodeRequest):
    """Геокодирование адреса"""
    try:
        results = await geocoding_service.geocode_address(
            request.address, 
            request.country, 
            request.limit
        )
        
        return GeocodeResponse(
            query=request.address,
            results=results,
            total_found=len(results)
        )
        
    except Exception as e:
        logger.error(f"Geocoding error: {e}")
        raise HTTPException(status_code=500, detail="Ошибка геокодирования")


@app.post("/reverse-geocode")
async def reverse_geocode(coordinates: Coordinates):
    """Обратное геокодирование"""
    try:
        result = await geocoding_service.reverse_geocode(
            coordinates.latitude, 
            coordinates.longitude
        )
        return result
        
    except Exception as e:
        logger.error(f"Reverse geocoding error: {e}")
        raise HTTPException(status_code=500, detail="Ошибка обратного геокодирования")


@app.post("/distance")
async def calculate_distance(request: DistanceRequest):
    """Расчет расстояния между точками"""
    try:
        distance_m = geometry_service.haversine_distance(
            request.point1.latitude, request.point1.longitude,
            request.point2.latitude, request.point2.longitude
        )
        
        # Конвертируем в нужные единицы
        if request.unit == "kilometers":
            distance = distance_m / 1000
        elif request.unit == "miles":
            distance = distance_m / 1609.34
        else:
            distance = distance_m
        
        return {
            "distance": round(distance, 2),
            "unit": request.unit,
            "distance_meters": distance_m
        }
        
    except Exception as e:
        logger.error(f"Distance calculation error: {e}")
        raise HTTPException(status_code=500, detail="Ошибка расчета расстояния")


@app.post("/area")
async def calculate_area(request: AreaRequest):
    """Расчет площади полигона"""
    try:
        area_sqm = geometry_service.calculate_polygon_area(request.coordinates)
        
        # Конвертируем в нужные единицы
        if request.unit == "sqkm":
            area = area_sqm / 1000000
        elif request.unit == "hectares":
            area = area_sqm / 10000
        else:
            area = area_sqm
        
        return {
            "area": round(area, 2),
            "unit": request.unit,
            "area_sqm": area_sqm
        }
        
    except Exception as e:
        logger.error(f"Area calculation error: {e}")
        raise HTTPException(status_code=500, detail="Ошибка расчета площади")


@app.get("/projects/{project_id}/geodata", response_model=ProjectGeoData)
async def get_project_geodata(project_id: str):
    """Получение геоданных проекта"""
    geodata = await storage.load_project_geodata(project_id)
    if not geodata:
        raise HTTPException(status_code=404, detail="Геоданные проекта не найдены")
    return geodata


@app.post("/projects/{project_id}/geodata")
async def save_project_geodata(project_id: str, geodata: ProjectGeoData):
    """Сохранение геоданных проекта"""
    geodata.project_id = project_id
    
    # Вычисляем дополнительные параметры
    all_coordinates = []
    
    # Собираем все координаты для расчета границ и центра
    for point in geodata.points:
        all_coordinates.append(point.coordinates)
    
    for polygon in geodata.polygons:
        for ring in polygon.coordinates:
            all_coordinates.extend(ring)
        
        # Вычисляем площадь полигона
        if polygon.coordinates and polygon.coordinates[0]:
            polygon.area_sqm = geometry_service.calculate_polygon_area(polygon.coordinates[0])
    
    for line in geodata.lines:
        all_coordinates.extend(line.coordinates)
        # Вычисляем длину линии
        line.length_m = geometry_service.calculate_line_length(line.coordinates)
    
    # Вычисляем границы и центр
    if all_coordinates:
        geodata.bounds = geometry_service.calculate_bounds(all_coordinates)
        geodata.center = geometry_service.calculate_center(all_coordinates)
    
    success = await storage.save_project_geodata(project_id, geodata)
    if not success:
        raise HTTPException(status_code=500, detail="Ошибка сохранения геоданных")
    
    return {"status": "success", "message": "Геоданные сохранены"}


@app.delete("/projects/{project_id}/geodata")
async def delete_project_geodata(project_id: str):
    """Удаление геоданных проекта"""
    success = await storage.delete_project_geodata(project_id)
    if not success:
        raise HTTPException(status_code=500, detail="Ошибка удаления геоданных")
    
    return {"status": "success", "message": "Геоданные удалены"}


@app.post("/projects/{project_id}/points")
async def add_project_point(project_id: str, point: GeoPoint):
    """Добавление точки к проекту"""
    geodata = await storage.load_project_geodata(project_id)
    if not geodata:
        geodata = ProjectGeoData(project_id=project_id)
    
    geodata.points.append(point)
    
    success = await storage.save_project_geodata(project_id, geodata)
    if not success:
        raise HTTPException(status_code=500, detail="Ошибка сохранения точки")
    
    return {"status": "success", "point_id": point.id}


@app.post("/projects/{project_id}/polygons")
async def add_project_polygon(project_id: str, polygon: GeoPolygon):
    """Добавление полигона к проекту"""
    geodata = await storage.load_project_geodata(project_id)
    if not geodata:
        geodata = ProjectGeoData(project_id=project_id)
    
    # Вычисляем площадь
    if polygon.coordinates and polygon.coordinates[0]:
        polygon.area_sqm = geometry_service.calculate_polygon_area(polygon.coordinates[0])
    
    geodata.polygons.append(polygon)
    
    success = await storage.save_project_geodata(project_id, geodata)
    if not success:
        raise HTTPException(status_code=500, detail="Ошибка сохранения полигона")
    
    return {"status": "success", "polygon_id": polygon.id}


@app.get("/projects/{project_id}/export")
async def export_project_geodata(project_id: str, format: str = "geojson"):
    """Экспорт геоданных проекта в различных форматах"""
    geodata = await storage.load_project_geodata(project_id)
    if not geodata:
        raise HTTPException(status_code=404, detail="Геоданные проекта не найдены")
    
    if format.lower() == "geojson":
        # Преобразуем в формат GeoJSON
        features = []
        
        # Добавляем точки
        for point in geodata.points:
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [point.coordinates.longitude, point.coordinates.latitude]
                },
                "properties": {
                    "id": point.id,
                    **point.properties
                }
            })
        
        # Добавляем полигоны
        for polygon in geodata.polygons:
            coordinates = []
            for ring in polygon.coordinates:
                ring_coords = [[coord.longitude, coord.latitude] for coord in ring]
                coordinates.append(ring_coords)
            
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": coordinates
                },
                "properties": {
                    "id": polygon.id,
                    "area_sqm": polygon.area_sqm,
                    **polygon.properties
                }
            })
        
        # Добавляем линии
        for line in geodata.lines:
            coordinates = [[coord.longitude, coord.latitude] for coord in line.coordinates]
            
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": coordinates
                },
                "properties": {
                    "id": line.id,
                    "length_m": line.length_m,
                    **line.properties
                }
            })
        
        geojson = {
            "type": "FeatureCollection",
            "features": features,
            "properties": {
                "project_id": project_id,
                "bounds": geodata.bounds,
                "center": geodata.center.dict() if geodata.center else None
            }
        }
        
        return geojson
    
    else:
        raise HTTPException(status_code=400, detail="Неподдерживаемый формат экспорта")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )
