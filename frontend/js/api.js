/**
 * API клиент для взаимодействия с backend сервисами
 * Электронный журнал производства работ
 */

class ApiClient {
    constructor() {
        this.baseUrl = '/api/v1';
        this.fileServiceUrl = '/files/v1';
        this.gisServiceUrl = '/gis/v1';
        this.token = localStorage.getItem('auth_token');
    }

    /**
     * Установка токена авторизации
     */
    setAuthToken(token) {
        this.token = token;
        if (token) {
            localStorage.setItem('auth_token', token);
        } else {
            localStorage.removeItem('auth_token');
        }
    }

    /**
     * Получение заголовков запроса
     */
    getHeaders(includeAuth = true, contentType = 'application/json') {
        const headers = {};
        
        if (contentType) {
            headers['Content-Type'] = contentType;
        }
        
        if (includeAuth && this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        
        return headers;
    }

    /**
     * Универсальный метод для API запросов
     */
    async request(url, options = {}) {
        const config = {
            method: 'GET',
            headers: this.getHeaders(),
            ...options
        };

        // Для FormData не устанавливаем Content-Type
        if (config.body instanceof FormData) {
            delete config.headers['Content-Type'];
        } else if (config.body && typeof config.body === 'object') {
            config.body = JSON.stringify(config.body);
        }

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                await this.handleErrorResponse(response);
            }

            // Проверяем, есть ли содержимое в ответе
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            }
            
            return response;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    /**
     * Обработка ошибок ответа
     */
    async handleErrorResponse(response) {
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        
        try {
            const errorData = await response.json();
            errorMessage = errorData.message || errorData.detail || errorMessage;
        } catch (e) {
            // Игнорируем ошибки парсинга JSON
        }

        if (response.status === 401) {
            this.setAuthToken(null);
            window.location.href = '/login.html';
            return;
        }

        throw new Error(errorMessage);
    }

    // ==========================================================================
    // МЕТОДЫ АВТОРИЗАЦИИ
    // ==========================================================================

    /**
     * Вход в систему
     */
    async login(username, password, organizationCode = null) {
        const data = { username, password };
        if (organizationCode) {
            data.organization_code = organizationCode;
        }

        const response = await this.request(`${this.baseUrl}/auth/login`, {
            method: 'POST',
            body: data,
            headers: this.getHeaders(false)
        });

        if (response.access_token) {
            this.setAuthToken(response.access_token);
        }

        return response;
    }

    /**
     * Выход из системы
     */
    async logout() {
        try {
            await this.request(`${this.baseUrl}/auth/logout`, {
                method: 'POST'
            });
        } finally {
            this.setAuthToken(null);
        }
    }

    /**
     * Получение информации о текущем пользователе
     */
    async getCurrentUser() {
        return await this.request(`${this.baseUrl}/auth/me`);
    }

    /**
     * Обновление токена
     */
    async refreshToken() {
        const response = await this.request(`${this.baseUrl}/auth/refresh`, {
            method: 'POST'
        });
        
        if (response.access_token) {
            this.setAuthToken(response.access_token);
        }
        
        return response;
    }

    // ==========================================================================
    // МЕТОДЫ ПОЛЬЗОВАТЕЛЕЙ
    // ==========================================================================

    /**
     * Создание пользователя
     */
    async createUser(userData) {
        return await this.request(`${this.baseUrl}/users/`, {
            method: 'POST',
            body: userData
        });
    }

    /**
     * Получение списка пользователей
     */
    async getUsers(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return await this.request(`${this.baseUrl}/users/?${queryString}`);
    }

    /**
     * Получение пользователя по ID
     */
    async getUser(userId) {
        return await this.request(`${this.baseUrl}/users/${userId}`);
    }

    /**
     * Обновление пользователя
     */
    async updateUser(userId, userData) {
        return await this.request(`${this.baseUrl}/users/${userId}`, {
            method: 'PUT',
            body: userData
        });
    }

    /**
     * Удаление пользователя
     */
    async deleteUser(userId) {
        return await this.request(`${this.baseUrl}/users/${userId}`, {
            method: 'DELETE'
        });
    }

    // ==========================================================================
    // МЕТОДЫ ОРГАНИЗАЦИЙ
    // ==========================================================================

    /**
     * Создание организации
     */
    async createOrganization(orgData) {
        return await this.request(`${this.baseUrl}/organizations/`, {
            method: 'POST',
            body: orgData
        });
    }

    /**
     * Получение списка организаций
     */
    async getOrganizations(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return await this.request(`${this.baseUrl}/organizations/?${queryString}`);
    }

    /**
     * Получение организации по ID
     */
    async getOrganization(orgId) {
        return await this.request(`${this.baseUrl}/organizations/${orgId}`);
    }

    // ==========================================================================
    // МЕТОДЫ ПРОЕКТОВ
    // ==========================================================================

    /**
     * Создание проекта
     */
    async createProject(projectData) {
        return await this.request(`${this.baseUrl}/projects/`, {
            method: 'POST',
            body: projectData
        });
    }

    /**
     * Получение списка проектов
     */
    async getProjects(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return await this.request(`${this.baseUrl}/projects/?${queryString}`);
    }

    /**
     * Получение проекта по ID
     */
    async getProject(projectId) {
        return await this.request(`${this.baseUrl}/projects/${projectId}`);
    }

    /**
     * Обновление проекта
     */
    async updateProject(projectId, projectData) {
        return await this.request(`${this.baseUrl}/projects/${projectId}`, {
            method: 'PUT',
            body: projectData
        });
    }

    /**
     * Удаление проекта
     */
    async deleteProject(projectId) {
        return await this.request(`${this.baseUrl}/projects/${projectId}`, {
            method: 'DELETE'
        });
    }

    /**
     * Получение местоположений проектов для карты
     */
    async getProjectLocations() {
        return await this.request(`${this.baseUrl}/projects/locations`);
    }

    // ==========================================================================
    // МЕТОДЫ ЖУРНАЛА
    // ==========================================================================

    /**
     * Создание записи в журнале
     */
    async createJournalEntry(entryData) {
        return await this.request(`${this.baseUrl}/journal/`, {
            method: 'POST',
            body: entryData
        });
    }

    /**
     * Получение записей журнала
     */
    async getJournalEntries(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return await this.request(`${this.baseUrl}/journal/?${queryString}`);
    }

    /**
     * Получение записи журнала по ID
     */
    async getJournalEntry(entryId) {
        return await this.request(`${this.baseUrl}/journal/${entryId}`);
    }

    /**
     * Обновление записи журнала
     */
    async updateJournalEntry(entryId, entryData) {
        return await this.request(`${this.baseUrl}/journal/${entryId}`, {
            method: 'PUT',
            body: entryData
        });
    }

    /**
     * Удаление записи журнала
     */
    async deleteJournalEntry(entryId) {
        return await this.request(`${this.baseUrl}/journal/${entryId}`, {
            method: 'DELETE'
        });
    }

    // ==========================================================================
    // МЕТОДЫ ДОКУМЕНТОВ
    // ==========================================================================

    /**
     * Получение списка документов
     */
    async getDocuments(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return await this.request(`${this.baseUrl}/documents/?${queryString}`);
    }

    /**
     * Получение документа по ID
     */
    async getDocument(documentId) {
        return await this.request(`${this.baseUrl}/documents/${documentId}`);
    }

    /**
     * Создание документа
     */
    async createDocument(documentData) {
        return await this.request(`${this.baseUrl}/documents/`, {
            method: 'POST',
            body: documentData
        });
    }

    // ==========================================================================
    // МЕТОДЫ ФАЙЛОВОГО СЕРВИСА
    // ==========================================================================

    /**
     * Загрузка файла
     */
    async uploadFile(file, metadata = {}) {
        const formData = new FormData();
        formData.append('file', file);
        
        Object.keys(metadata).forEach(key => {
            formData.append(key, metadata[key]);
        });

        return await this.request(`${this.fileServiceUrl}/upload`, {
            method: 'POST',
            body: formData
        });
    }

    /**
     * Массовая загрузка файлов
     */
    async uploadFiles(files, metadata = {}) {
        const formData = new FormData();
        
        Array.from(files).forEach(file => {
            formData.append('files', file);
        });
        
        Object.keys(metadata).forEach(key => {
            formData.append(key, metadata[key]);
        });

        return await this.request(`${this.fileServiceUrl}/bulk-upload`, {
            method: 'POST',
            body: formData
        });
    }

    /**
     * Получение файла
     */
    async getFile(fileId) {
        return await this.request(`${this.fileServiceUrl}/files/${fileId}`);
    }

    /**
     * Скачивание файла
     */
    async downloadFile(fileId) {
        const response = await this.request(`${this.fileServiceUrl}/files/${fileId}/download`);
        return response;
    }

    /**
     * Удаление файла
     */
    async deleteFile(fileId) {
        return await this.request(`${this.fileServiceUrl}/files/${fileId}`, {
            method: 'DELETE'
        });
    }

    /**
     * Получение метаданных файла
     */
    async getFileMetadata(fileId) {
        return await this.request(`${this.fileServiceUrl}/files/${fileId}/metadata`);
    }

    // ==========================================================================
    // МЕТОДЫ ДАШБОРДА
    // ==========================================================================

    /**
     * Получение статистики для дашборда
     */
    async getDashboardStats() {
        return await this.request(`${this.baseUrl}/dashboard/stats`);
    }

    /**
     * Получение последних активностей
     */
    async getRecentActivities() {
        return await this.request(`${this.baseUrl}/dashboard/activities`);
    }

    /**
     * Получение данных для графиков
     */
    async getChartData(chartType = 'activity') {
        return await this.request(`${this.baseUrl}/dashboard/chart-data?type=${chartType}`);
    }

    // ==========================================================================
    // МЕТОДЫ УВЕДОМЛЕНИЙ
    // ==========================================================================

    /**
     * Получение уведомлений
     */
    async getNotifications(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return await this.request(`${this.baseUrl}/notifications/?${queryString}`);
    }

    /**
     * Отметка уведомления как прочитанного
     */
    async markNotificationAsRead(notificationId) {
        return await this.request(`${this.baseUrl}/notifications/${notificationId}/read`, {
            method: 'POST'
        });
    }

    /**
     * Отметка всех уведомлений как прочитанных
     */
    async markAllNotificationsAsRead() {
        return await this.request(`${this.baseUrl}/notifications/mark-all-read`, {
            method: 'POST'
        });
    }

    // ==========================================================================
    // МЕТОДЫ ОТЧЕТОВ
    // ==========================================================================

    /**
     * Генерация отчета
     */
    async generateReport(reportType, params = {}) {
        return await this.request(`${this.baseUrl}/reports/generate`, {
            method: 'POST',
            body: {
                type: reportType,
                parameters: params
            }
        });
    }

    /**
     * Получение списка доступных отчетов
     */
    async getAvailableReports() {
        return await this.request(`${this.baseUrl}/reports/templates`);
    }

    /**
     * Скачивание отчета
     */
    async downloadReport(reportId) {
        return await this.request(`${this.baseUrl}/reports/${reportId}/download`);
    }

    // ==========================================================================
    // GIS МЕТОДЫ
    // ==========================================================================

    /**
     * Получение геоданных проекта
     */
    async getProjectGeoData(projectId) {
        return await this.request(`${this.gisServiceUrl}/projects/${projectId}/geodata`);
    }

    /**
     * Сохранение геоданных
     */
    async saveGeoData(geoData) {
        return await this.request(`${this.gisServiceUrl}/geodata`, {
            method: 'POST',
            body: geoData
        });
    }

    /**
     * Геокодирование адреса
     */
    async geocodeAddress(address) {
        return await this.request(`${this.gisServiceUrl}/geocode?address=${encodeURIComponent(address)}`);
    }

    // ==========================================================================
    // МЕТОДЫ ПОИСКА
    // ==========================================================================

    /**
     * Глобальный поиск
     */
    async search(query, params = {}) {
        const searchParams = new URLSearchParams({
            q: query,
            ...params
        }).toString();
        
        return await this.request(`${this.baseUrl}/search?${searchParams}`);
    }

    /**
     * Поиск в журнале
     */
    async searchJournal(query, filters = {}) {
        return await this.request(`${this.baseUrl}/journal/search`, {
            method: 'POST',
            body: {
                query,
                filters
            }
        });
    }
}

// Экспорт класса
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ApiClient;
} else {
    window.ApiClient = ApiClient;
}
