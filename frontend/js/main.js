/**
 * Главный JavaScript файл для Электронного журнала производства работ
 * Промышленное решение для государственных контролирующих органов
 */

class ElectronicJournal {
    constructor() {
        this.init();
        this.config = {
            apiBaseUrl: '/api/v1',
            fileServiceUrl: '/files/v1',
            wsUrl: 'ws://localhost:8001/ws',
            version: '1.0.0'
        };
        this.user = null;
        this.organization = null;
        this.currentProject = null;
        this.socket = null;
        this.charts = {};
        this.map = null;
    }

    /**
     * Инициализация приложения
     */
    async init() {
        try {
            // Показываем loading screen
            this.showLoadingScreen();
            
            // Инициализируем Service Worker для PWA
            await this.initServiceWorker();
            
            // Проверяем авторизацию
            await this.checkAuth();
            
            // Инициализируем компоненты
            await this.initComponents();
            
            // Инициализируем WebSocket соединение
            await this.initWebSocket();
            
            // Скрываем loading screen
            this.hideLoadingScreen();
            
            console.log('Electronic Journal initialized successfully');
        } catch (error) {
            console.error('Failed to initialize Electronic Journal:', error);
            this.showError('Ошибка инициализации приложения');
        }
    }

    /**
     * Показать экран загрузки
     */
    showLoadingScreen() {
        const loadingScreen = document.getElementById('loading-screen');
        if (loadingScreen) {
            loadingScreen.style.display = 'flex';
        }
    }

    /**
     * Скрыть экран загрузки
     */
    hideLoadingScreen() {
        const loadingScreen = document.getElementById('loading-screen');
        if (loadingScreen) {
            loadingScreen.classList.add('fade-out');
            setTimeout(() => {
                loadingScreen.style.display = 'none';
            }, 300);
        }
    }

    /**
     * Инициализация Service Worker
     */
    async initServiceWorker() {
        if ('serviceWorker' in navigator) {
            try {
                const registration = await navigator.serviceWorker.register('/sw.js');
                console.log('Service Worker registered:', registration);
            } catch (error) {
                console.error('Service Worker registration failed:', error);
            }
        }
    }

    /**
     * Проверка авторизации пользователя
     */
    async checkAuth() {
        const token = localStorage.getItem('auth_token');
        if (!token) {
            this.redirectToLogin();
            return;
        }

        try {
            const response = await this.apiRequest('/auth/me', 'GET');
            this.user = response.user;
            this.organization = response.organization;
            this.updateUserInterface();
        } catch (error) {
            console.error('Auth check failed:', error);
            this.redirectToLogin();
        }
    }

    /**
     * Перенаправление на страницу входа
     */
    redirectToLogin() {
        window.location.href = '/login.html';
    }

    /**
     * Обновление пользовательского интерфейса
     */
    updateUserInterface() {
        if (this.user) {
            // Обновляем информацию о пользователе в навбаре
            const userInfo = document.getElementById('user-info');
            if (userInfo) {
                userInfo.innerHTML = `
                    <img src="${this.user.avatar || '/images/default-avatar.png'}" 
                         alt="${this.user.full_name}" 
                         class="rounded-circle me-2" 
                         width="32" height="32">
                    <span class="d-none d-md-inline">${this.user.full_name}</span>
                `;
            }

            // Обновляем информацию об организации
            const orgInfo = document.getElementById('org-info');
            if (orgInfo && this.organization) {
                orgInfo.textContent = this.organization.name;
            }
        }
    }

    /**
     * Инициализация компонентов
     */
    async initComponents() {
        // Инициализация навигации
        this.initNavigation();
        
        // Инициализация модальных окон
        this.initModals();
        
        // Инициализация форм
        this.initForms();
        
        // Инициализация tooltips и popovers
        this.initBootstrapComponents();
        
        // Инициализация drag & drop
        this.initDragAndDrop();
        
        // Загружаем начальную страницу
        await this.loadPage('dashboard');
    }

    /**
     * Инициализация навигации
     */
    initNavigation() {
        // Обработчики клика по навигационным ссылкам
        document.querySelectorAll('[data-page]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = e.target.closest('[data-page]').dataset.page;
                this.loadPage(page);
            });
        });

        // Обработчик выхода
        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => this.logout());
        }
    }

    /**
     * Загрузка страницы
     */
    async loadPage(pageName) {
        try {
            const contentContainer = document.getElementById('page-content');
            if (!contentContainer) return;

            // Показываем индикатор загрузки
            contentContainer.innerHTML = '<div class="text-center p-4"><div class="spinner-border" role="status"></div></div>';

            // Обновляем активную навигацию
            this.updateActiveNavigation(pageName);

            // Загружаем контент страницы
            let content = '';
            switch (pageName) {
                case 'dashboard':
                    content = await this.loadDashboard();
                    break;
                case 'projects':
                    content = await this.loadProjects();
                    break;
                case 'journal':
                    content = await this.loadJournal();
                    break;
                case 'documents':
                    content = await this.loadDocuments();
                    break;
                case 'reports':
                    content = await this.loadReports();
                    break;
                case 'maps':
                    content = await this.loadMaps();
                    break;
                case 'settings':
                    content = await this.loadSettings();
                    break;
                default:
                    content = '<div class="alert alert-warning">Страница не найдена</div>';
            }

            contentContainer.innerHTML = content;

            // Инициализируем компоненты для загруженной страницы
            await this.initPageComponents(pageName);

        } catch (error) {
            console.error('Failed to load page:', error);
            this.showError('Ошибка загрузки страницы');
        }
    }

    /**
     * Обновление активной навигации
     */
    updateActiveNavigation(pageName) {
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        
        const activeLink = document.querySelector(`[data-page="${pageName}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
        }
    }

    /**
     * Загрузка дашборда
     */
    async loadDashboard() {
        const stats = await this.apiRequest('/dashboard/stats');
        const recentActivities = await this.apiRequest('/dashboard/activities');

        return `
            <div class="container-fluid p-4">
                <div class="row mb-4">
                    <div class="col-12">
                        <h1 class="h3 mb-0">Панель управления</h1>
                        <p class="text-muted">Обзор текущего состояния проектов</p>
                    </div>
                </div>

                <div class="row mb-4">
                    ${this.renderStatsCards(stats)}
                </div>

                <div class="row">
                    <div class="col-lg-8">
                        <div class="card">
                            <div class="card-header">
                                <h5 class="card-title mb-0">Активность проектов</h5>
                            </div>
                            <div class="card-body">
                                <canvas id="activity-chart" width="400" height="200"></canvas>
                            </div>
                        </div>
                    </div>
                    <div class="col-lg-4">
                        <div class="card">
                            <div class="card-header">
                                <h5 class="card-title mb-0">Последние события</h5>
                            </div>
                            <div class="card-body">
                                ${this.renderRecentActivities(recentActivities)}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Отрисовка карточек статистики
     */
    renderStatsCards(stats) {
        const cards = [
            { title: 'Активные проекты', value: stats.active_projects, icon: 'bi-clipboard-check', color: 'primary' },
            { title: 'Записи в журнале', value: stats.journal_entries, icon: 'bi-journal-text', color: 'success' },
            { title: 'Документы', value: stats.documents, icon: 'bi-file-earmark-text', color: 'info' },
            { title: 'Уведомления', value: stats.notifications, icon: 'bi-bell', color: 'warning' }
        ];

        return cards.map(card => `
            <div class="col-xl-3 col-lg-6 col-md-6 mb-3">
                <div class="card border-0 shadow-sm">
                    <div class="card-body">
                        <div class="d-flex align-items-center">
                            <div class="flex-shrink-0">
                                <div class="bg-${card.color} text-white rounded-circle d-flex align-items-center justify-content-center" style="width: 50px; height: 50px;">
                                    <i class="${card.icon}"></i>
                                </div>
                            </div>
                            <div class="flex-grow-1 ms-3">
                                <h6 class="text-muted mb-1">${card.title}</h6>
                                <h4 class="mb-0">${card.value}</h4>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    /**
     * Отрисовка последних событий
     */
    renderRecentActivities(activities) {
        if (!activities || activities.length === 0) {
            return '<p class="text-muted">Нет недавних событий</p>';
        }

        return activities.map(activity => `
            <div class="d-flex align-items-center mb-3">
                <div class="flex-shrink-0">
                    <div class="bg-light rounded-circle d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;">
                        <i class="bi-${activity.icon} text-primary"></i>
                    </div>
                </div>
                <div class="flex-grow-1 ms-3">
                    <h6 class="mb-1">${activity.title}</h6>
                    <p class="text-muted small mb-0">${activity.description}</p>
                    <small class="text-muted">${this.formatDate(activity.created_at)}</small>
                </div>
            </div>
        `).join('');
    }

    /**
     * Инициализация компонентов для страницы
     */
    async initPageComponents(pageName) {
        switch (pageName) {
            case 'dashboard':
                await this.initDashboardCharts();
                break;
            case 'maps':
                await this.initMap();
                break;
            case 'journal':
                this.initJournalFilters();
                break;
        }
    }

    /**
     * Инициализация графиков дашборда
     */
    async initDashboardCharts() {
        const activityCanvas = document.getElementById('activity-chart');
        if (activityCanvas) {
            const data = await this.apiRequest('/dashboard/chart-data');
            
            this.charts.activity = new Chart(activityCanvas, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Записи в журнале',
                        data: data.values,
                        borderColor: '#0d6efd',
                        backgroundColor: 'rgba(13, 110, 253, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
    }

    /**
     * Инициализация карты
     */
    async initMap() {
        const mapContainer = document.getElementById('map');
        if (mapContainer) {
            this.map = L.map('map').setView([55.7558, 37.6176], 10);
            
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors'
            }).addTo(this.map);

            // Загружаем маркеры проектов
            const projects = await this.apiRequest('/projects/locations');
            projects.forEach(project => {
                if (project.latitude && project.longitude) {
                    L.marker([project.latitude, project.longitude])
                        .addTo(this.map)
                        .bindPopup(`
                            <strong>${project.name}</strong><br>
                            ${project.address}<br>
                            Статус: ${project.status}
                        `);
                }
            });
        }
    }

    /**
     * Инициализация WebSocket соединения
     */
    async initWebSocket() {
        try {
            this.socket = io(this.config.wsUrl, {
                auth: {
                    token: localStorage.getItem('auth_token')
                }
            });

            this.socket.on('connect', () => {
                console.log('WebSocket connected');
            });

            this.socket.on('disconnect', () => {
                console.log('WebSocket disconnected');
            });

            this.socket.on('notification', (data) => {
                this.showNotification(data);
            });

            this.socket.on('journal_update', (data) => {
                this.handleJournalUpdate(data);
            });

        } catch (error) {
            console.error('WebSocket initialization failed:', error);
        }
    }

    /**
     * Инициализация модальных окон
     */
    initModals() {
        // Обработчики для модальных окон
        document.addEventListener('show.bs.modal', (e) => {
            const modal = e.target;
            const form = modal.querySelector('form');
            if (form) {
                form.reset();
            }
        });
    }

    /**
     * Инициализация форм
     */
    initForms() {
        // Обработчик отправки форм
        document.addEventListener('submit', (e) => {
            const form = e.target;
            if (form.classList.contains('ajax-form')) {
                e.preventDefault();
                this.handleFormSubmit(form);
            }
        });
    }

    /**
     * Обработка отправки форм
     */
    async handleFormSubmit(form) {
        try {
            const submitBtn = form.querySelector('[type="submit"]');
            const originalText = submitBtn.textContent;
            
            // Показываем индикатор загрузки
            submitBtn.classList.add('loading');
            submitBtn.disabled = true;

            const formData = new FormData(form);
            const url = form.action || form.dataset.action;
            const method = form.method || 'POST';

            const response = await this.apiRequest(url, method, formData);

            // Показываем успешное сообщение
            this.showSuccess(response.message || 'Операция выполнена успешно');

            // Закрываем модальное окно если есть
            const modal = form.closest('.modal');
            if (modal) {
                const bsModal = bootstrap.Modal.getInstance(modal);
                if (bsModal) {
                    bsModal.hide();
                }
            }

            // Обновляем страницу если нужно
            if (form.dataset.reload === 'true') {
                const currentPage = document.querySelector('.nav-link.active')?.dataset.page || 'dashboard';
                await this.loadPage(currentPage);
            }

        } catch (error) {
            console.error('Form submission failed:', error);
            this.showError(error.message || 'Ошибка отправки формы');
        } finally {
            const submitBtn = form.querySelector('[type="submit"]');
            submitBtn.classList.remove('loading');
            submitBtn.disabled = false;
        }
    }

    /**
     * Инициализация Bootstrap компонентов
     */
    initBootstrapComponents() {
        // Tooltips
        const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        tooltips.forEach(tooltip => {
            new bootstrap.Tooltip(tooltip);
        });

        // Popovers
        const popovers = document.querySelectorAll('[data-bs-toggle="popover"]');
        popovers.forEach(popover => {
            new bootstrap.Popover(popover);
        });
    }

    /**
     * Инициализация drag & drop
     */
    initDragAndDrop() {
        document.addEventListener('dragover', (e) => {
            e.preventDefault();
            const dropZone = e.target.closest('.custom-file-upload');
            if (dropZone) {
                dropZone.classList.add('dragover');
            }
        });

        document.addEventListener('dragleave', (e) => {
            const dropZone = e.target.closest('.custom-file-upload');
            if (dropZone && !dropZone.contains(e.relatedTarget)) {
                dropZone.classList.remove('dragover');
            }
        });

        document.addEventListener('drop', (e) => {
            e.preventDefault();
            const dropZone = e.target.closest('.custom-file-upload');
            if (dropZone) {
                dropZone.classList.remove('dragover');
                const files = e.dataTransfer.files;
                this.handleFileUpload(files);
            }
        });
    }

    /**
     * Обработка загрузки файлов
     */
    async handleFileUpload(files) {
        const formData = new FormData();
        Array.from(files).forEach(file => {
            formData.append('files', file);
        });

        try {
            const response = await fetch(`${this.config.fileServiceUrl}/upload`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
                },
                body: formData
            });

            if (!response.ok) {
                throw new Error('Upload failed');
            }

            const result = await response.json();
            this.showSuccess('Файлы успешно загружены');
            
            // Обновляем список файлов если на странице документов
            const currentPage = document.querySelector('.nav-link.active')?.dataset.page;
            if (currentPage === 'documents') {
                await this.loadPage('documents');
            }

        } catch (error) {
            console.error('File upload failed:', error);
            this.showError('Ошибка загрузки файлов');
        }
    }

    /**
     * API запрос
     */
    async apiRequest(url, method = 'GET', body = null) {
        const token = localStorage.getItem('auth_token');
        const headers = {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        };

        // Если body это FormData, удаляем Content-Type
        if (body instanceof FormData) {
            delete headers['Content-Type'];
        } else if (body) {
            body = JSON.stringify(body);
        }

        const response = await fetch(`${this.config.apiBaseUrl}${url}`, {
            method,
            headers,
            body
        });

        if (!response.ok) {
            if (response.status === 401) {
                this.redirectToLogin();
                return;
            }
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return await response.json();
    }

    /**
     * Показать уведомление об успехе
     */
    showSuccess(message) {
        this.showToast(message, 'success');
    }

    /**
     * Показать ошибку
     */
    showError(message) {
        this.showToast(message, 'danger');
    }

    /**
     * Показать toast уведомление
     */
    showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toast-container');
        if (!toastContainer) return;

        const toastId = 'toast-' + Date.now();
        const toastHtml = `
            <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-header">
                    <div class="rounded me-2 bg-${type}" style="width: 20px; height: 20px;"></div>
                    <strong class="me-auto">Уведомление</strong>
                    <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            </div>
        `;

        toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement);
        toast.show();

        // Удаляем элемент после скрытия
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }

    /**
     * Обработка обновлений журнала
     */
    handleJournalUpdate(data) {
        // Если мы на странице журнала, обновляем содержимое
        const currentPage = document.querySelector('.nav-link.active')?.dataset.page;
        if (currentPage === 'journal') {
            this.loadPage('journal');
        }
    }

    /**
     * Форматирование даты
     */
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString('ru-RU');
    }

    /**
     * Выход из системы
     */
    async logout() {
        try {
            await this.apiRequest('/auth/logout', 'POST');
        } catch (error) {
            console.error('Logout failed:', error);
        } finally {
            localStorage.removeItem('auth_token');
            window.location.href = '/login.html';
        }
    }

    /**
     * Загрузка проектов (заглушка)
     */
    async loadProjects() {
        return `
            <div class="container-fluid p-4">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h1 class="h3 mb-0">Проекты</h1>
                    <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#createProjectModal">
                        <i class="bi-plus"></i> Создать проект
                    </button>
                </div>
                <div class="card">
                    <div class="card-body">
                        <p>Список проектов будет здесь...</p>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Загрузка журнала (заглушка)
     */
    async loadJournal() {
        return `
            <div class="container-fluid p-4">
                <h1 class="h3 mb-4">Журнал производства работ</h1>
                <div class="card">
                    <div class="card-body">
                        <p>Записи журнала будут здесь...</p>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Загрузка документов (заглушка)
     */
    async loadDocuments() {
        return `
            <div class="container-fluid p-4">
                <h1 class="h3 mb-4">Документы</h1>
                <div class="card">
                    <div class="card-body">
                        <div class="custom-file-upload text-center p-4">
                            <i class="bi-cloud-upload display-1 text-muted"></i>
                            <p>Перетащите файлы сюда или нажмите для выбора</p>
                            <input type="file" class="d-none" id="file-input" multiple>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Загрузка отчетов (заглушка)
     */
    async loadReports() {
        return `
            <div class="container-fluid p-4">
                <h1 class="h3 mb-4">Отчеты</h1>
                <div class="card">
                    <div class="card-body">
                        <p>Отчеты будут здесь...</p>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Загрузка карт (заглушка)
     */
    async loadMaps() {
        return `
            <div class="container-fluid p-4">
                <h1 class="h3 mb-4">Карты</h1>
                <div class="card">
                    <div class="card-body">
                        <div id="map" class="map-container"></div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Загрузка настроек (заглушка)
     */
    async loadSettings() {
        return `
            <div class="container-fluid p-4">
                <h1 class="h3 mb-4">Настройки</h1>
                <div class="card">
                    <div class="card-body">
                        <p>Настройки будут здесь...</p>
                    </div>
                </div>
            </div>
        `;
    }
}

// Инициализация приложения при загрузке DOM
document.addEventListener('DOMContentLoaded', () => {
    window.app = new ElectronicJournal();
});

// Экспорт для тестирования
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ElectronicJournal;
}
