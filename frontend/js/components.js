/**
 * Компоненты для Электронного журнала производства работ
 * Переиспользуемые UI компоненты
 */

class ComponentManager {
    constructor() {
        this.components = new Map();
        this.init();
    }

    init() {
        this.registerComponent('modal', ModalComponent);
        this.registerComponent('table', TableComponent);
        this.registerComponent('form', FormComponent);
        this.registerComponent('chart', ChartComponent);
        this.registerComponent('map', MapComponent);
        this.registerComponent('fileUpload', FileUploadComponent);
        this.registerComponent('search', SearchComponent);
        this.registerComponent('notification', NotificationComponent);
    }

    registerComponent(name, componentClass) {
        this.components.set(name, componentClass);
    }

    createComponent(name, options = {}) {
        const ComponentClass = this.components.get(name);
        if (!ComponentClass) {
            throw new Error(`Component ${name} not found`);
        }
        return new ComponentClass(options);
    }
}

// ==========================================================================
// БАЗОВЫЙ КОМПОНЕНТ
// ==========================================================================

class BaseComponent {
    constructor(options = {}) {
        this.options = { ...this.defaultOptions, ...options };
        this.element = null;
        this.events = new Map();
    }

    get defaultOptions() {
        return {};
    }

    render() {
        throw new Error('render method must be implemented');
    }

    mount(container) {
        if (typeof container === 'string') {
            container = document.querySelector(container);
        }
        if (!container) {
            throw new Error('Container not found');
        }

        this.element = this.render();
        container.appendChild(this.element);
        this.afterMount();
        return this;
    }

    afterMount() {
        // Переопределяется в наследниках
    }

    on(event, handler) {
        if (!this.events.has(event)) {
            this.events.set(event, []);
        }
        this.events.get(event).push(handler);
        return this;
    }

    emit(event, data = null) {
        if (this.events.has(event)) {
            this.events.get(event).forEach(handler => handler(data));
        }
        return this;
    }

    destroy() {
        if (this.element && this.element.parentNode) {
            this.element.parentNode.removeChild(this.element);
        }
        this.events.clear();
    }
}

// ==========================================================================
// МОДАЛЬНОЕ ОКНО
// ==========================================================================

class ModalComponent extends BaseComponent {
    get defaultOptions() {
        return {
            title: 'Модальное окно',
            size: 'lg', // sm, lg, xl
            backdrop: true,
            keyboard: true,
            footer: true,
            closeButton: true
        };
    }

    render() {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.tabIndex = -1;
        modal.setAttribute('aria-hidden', 'true');

        modal.innerHTML = `
            <div class="modal-dialog modal-${this.options.size}">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${this.options.title}</h5>
                        ${this.options.closeButton ? '<button type="button" class="btn-close" data-bs-dismiss="modal"></button>' : ''}
                    </div>
                    <div class="modal-body">
                        <!-- Контент будет добавлен динамически -->
                    </div>
                    ${this.options.footer ? '<div class="modal-footer"></div>' : ''}
                </div>
            </div>
        `;

        this.bsModal = new bootstrap.Modal(modal, {
            backdrop: this.options.backdrop,
            keyboard: this.options.keyboard
        });

        return modal;
    }

    afterMount() {
        this.element.addEventListener('hidden.bs.modal', () => {
            this.emit('hidden');
        });

        this.element.addEventListener('shown.bs.modal', () => {
            this.emit('shown');
        });
    }

    setTitle(title) {
        const titleElement = this.element.querySelector('.modal-title');
        if (titleElement) {
            titleElement.textContent = title;
        }
        return this;
    }

    setBody(content) {
        const bodyElement = this.element.querySelector('.modal-body');
        if (bodyElement) {
            if (typeof content === 'string') {
                bodyElement.innerHTML = content;
            } else {
                bodyElement.innerHTML = '';
                bodyElement.appendChild(content);
            }
        }
        return this;
    }

    setFooter(content) {
        const footerElement = this.element.querySelector('.modal-footer');
        if (footerElement) {
            if (typeof content === 'string') {
                footerElement.innerHTML = content;
            } else {
                footerElement.innerHTML = '';
                footerElement.appendChild(content);
            }
        }
        return this;
    }

    show() {
        this.bsModal.show();
        return this;
    }

    hide() {
        this.bsModal.hide();
        return this;
    }
}

// ==========================================================================
// ТАБЛИЦА
// ==========================================================================

class TableComponent extends BaseComponent {
    get defaultOptions() {
        return {
            columns: [],
            data: [],
            selectable: false,
            sortable: true,
            filterable: true,
            pagination: true,
            pageSize: 10,
            responsive: true,
            actions: []
        };
    }

    render() {
        const container = document.createElement('div');
        container.className = 'table-component';

        if (this.options.filterable) {
            const filterRow = this.createFilterRow();
            container.appendChild(filterRow);
        }

        const tableContainer = document.createElement('div');
        if (this.options.responsive) {
            tableContainer.className = 'table-responsive';
        }

        const table = document.createElement('table');
        table.className = 'table table-striped table-hover';

        // Создаем заголовок
        const thead = this.createTableHeader();
        table.appendChild(thead);

        // Создаем тело таблицы
        const tbody = this.createTableBody();
        table.appendChild(tbody);

        tableContainer.appendChild(table);
        container.appendChild(tableContainer);

        if (this.options.pagination) {
            const pagination = this.createPagination();
            container.appendChild(pagination);
        }

        return container;
    }

    createFilterRow() {
        const filterRow = document.createElement('div');
        filterRow.className = 'row mb-3';

        const col = document.createElement('div');
        col.className = 'col-md-6';

        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'form-control';
        input.placeholder = 'Поиск...';
        input.addEventListener('input', (e) => {
            this.filter(e.target.value);
        });

        col.appendChild(input);
        filterRow.appendChild(col);

        return filterRow;
    }

    createTableHeader() {
        const thead = document.createElement('thead');
        const tr = document.createElement('tr');

        if (this.options.selectable) {
            const th = document.createElement('th');
            th.innerHTML = '<input type="checkbox" class="select-all">';
            tr.appendChild(th);
        }

        this.options.columns.forEach(column => {
            const th = document.createElement('th');
            th.textContent = column.title;
            th.dataset.field = column.field;

            if (this.options.sortable && column.sortable !== false) {
                th.style.cursor = 'pointer';
                th.addEventListener('click', () => {
                    this.sort(column.field);
                });
            }

            tr.appendChild(th);
        });

        if (this.options.actions.length > 0) {
            const th = document.createElement('th');
            th.textContent = 'Действия';
            tr.appendChild(th);
        }

        thead.appendChild(tr);
        return thead;
    }

    createTableBody() {
        const tbody = document.createElement('tbody');
        this.renderData(tbody);
        return tbody;
    }

    renderData(tbody) {
        tbody.innerHTML = '';

        this.getCurrentPageData().forEach(row => {
            const tr = this.createTableRow(row);
            tbody.appendChild(tr);
        });
    }

    createTableRow(rowData) {
        const tr = document.createElement('tr');

        if (this.options.selectable) {
            const td = document.createElement('td');
            td.innerHTML = `<input type="checkbox" value="${rowData.id || ''}">`;
            tr.appendChild(td);
        }

        this.options.columns.forEach(column => {
            const td = document.createElement('td');
            let value = this.getNestedValue(rowData, column.field);

            if (column.render) {
                value = column.render(value, rowData);
            }

            if (typeof value === 'string') {
                td.innerHTML = value;
            } else {
                td.appendChild(value);
            }

            tr.appendChild(td);
        });

        if (this.options.actions.length > 0) {
            const td = document.createElement('td');
            td.className = 'table-actions';

            this.options.actions.forEach(action => {
                const btn = document.createElement('button');
                btn.className = `btn btn-sm btn-${action.variant || 'outline-primary'}`;
                btn.innerHTML = action.icon ? `<i class="${action.icon}"></i>` : action.text;
                btn.title = action.title || action.text;
                btn.addEventListener('click', () => {
                    action.handler(rowData);
                });
                td.appendChild(btn);
            });

            tr.appendChild(td);
        }

        return tr;
    }

    getNestedValue(obj, path) {
        return path.split('.').reduce((current, key) => current && current[key], obj);
    }

    getCurrentPageData() {
        if (!this.options.pagination) {
            return this.filteredData || this.options.data;
        }

        const data = this.filteredData || this.options.data;
        const start = (this.currentPage - 1) * this.options.pageSize;
        const end = start + this.options.pageSize;
        
        return data.slice(start, end);
    }

    createPagination() {
        // Упрощенная пагинация
        const nav = document.createElement('nav');
        nav.innerHTML = `
            <ul class="pagination justify-content-center">
                <li class="page-item">
                    <button class="page-link" id="prev-page">Предыдущая</button>
                </li>
                <li class="page-item">
                    <span class="page-link" id="page-info">1 из 1</span>
                </li>
                <li class="page-item">
                    <button class="page-link" id="next-page">Следующая</button>
                </li>
            </ul>
        `;

        return nav;
    }

    filter(query) {
        if (!query) {
            this.filteredData = null;
        } else {
            this.filteredData = this.options.data.filter(row => {
                return this.options.columns.some(column => {
                    const value = this.getNestedValue(row, column.field);
                    return value && value.toString().toLowerCase().includes(query.toLowerCase());
                });
            });
        }

        this.currentPage = 1;
        this.refresh();
    }

    sort(field) {
        // Простая сортировка
        const data = this.filteredData || this.options.data;
        data.sort((a, b) => {
            const aVal = this.getNestedValue(a, field);
            const bVal = this.getNestedValue(b, field);
            
            if (aVal < bVal) return -1;
            if (aVal > bVal) return 1;
            return 0;
        });

        this.refresh();
    }

    refresh() {
        const tbody = this.element.querySelector('tbody');
        if (tbody) {
            this.renderData(tbody);
        }
    }

    setData(data) {
        this.options.data = data;
        this.filteredData = null;
        this.currentPage = 1;
        this.refresh();
        return this;
    }
}

// ==========================================================================
// ФОРМА
// ==========================================================================

class FormComponent extends BaseComponent {
    get defaultOptions() {
        return {
            fields: [],
            submitText: 'Сохранить',
            resetText: 'Сбросить',
            showReset: true,
            horizontal: false,
            ajax: true
        };
    }

    render() {
        const form = document.createElement('form');
        form.className = this.options.ajax ? 'ajax-form' : '';

        this.options.fields.forEach(field => {
            const fieldElement = this.createField(field);
            form.appendChild(fieldElement);
        });

        // Кнопки
        const buttonGroup = document.createElement('div');
        buttonGroup.className = 'd-flex gap-2 mt-3';

        const submitBtn = document.createElement('button');
        submitBtn.type = 'submit';
        submitBtn.className = 'btn btn-primary';
        submitBtn.textContent = this.options.submitText;

        buttonGroup.appendChild(submitBtn);

        if (this.options.showReset) {
            const resetBtn = document.createElement('button');
            resetBtn.type = 'reset';
            resetBtn.className = 'btn btn-outline-secondary';
            resetBtn.textContent = this.options.resetText;
            buttonGroup.appendChild(resetBtn);
        }

        form.appendChild(buttonGroup);

        return form;
    }

    createField(field) {
        const container = document.createElement('div');
        container.className = 'mb-3';

        if (field.type !== 'hidden') {
            const label = document.createElement('label');
            label.className = 'form-label';
            label.textContent = field.label;
            label.setAttribute('for', field.name);
            container.appendChild(label);
        }

        let input;
        switch (field.type) {
            case 'textarea':
                input = this.createTextarea(field);
                break;
            case 'select':
                input = this.createSelect(field);
                break;
            case 'checkbox':
                input = this.createCheckbox(field);
                break;
            case 'radio':
                input = this.createRadio(field);
                break;
            case 'file':
                input = this.createFileInput(field);
                break;
            default:
                input = this.createInput(field);
        }

        container.appendChild(input);

        if (field.help) {
            const help = document.createElement('div');
            help.className = 'form-text';
            help.textContent = field.help;
            container.appendChild(help);
        }

        return container;
    }

    createInput(field) {
        const input = document.createElement('input');
        input.type = field.type || 'text';
        input.name = field.name;
        input.id = field.name;
        input.className = 'form-control';
        
        if (field.placeholder) input.placeholder = field.placeholder;
        if (field.required) input.required = true;
        if (field.value !== undefined) input.value = field.value;

        return input;
    }

    createTextarea(field) {
        const textarea = document.createElement('textarea');
        textarea.name = field.name;
        textarea.id = field.name;
        textarea.className = 'form-control';
        textarea.rows = field.rows || 3;
        
        if (field.placeholder) textarea.placeholder = field.placeholder;
        if (field.required) textarea.required = true;
        if (field.value !== undefined) textarea.value = field.value;

        return textarea;
    }

    createSelect(field) {
        const select = document.createElement('select');
        select.name = field.name;
        select.id = field.name;
        select.className = 'form-select';
        
        if (field.required) select.required = true;

        if (field.options) {
            field.options.forEach(option => {
                const opt = document.createElement('option');
                opt.value = option.value;
                opt.textContent = option.label;
                if (option.value === field.value) opt.selected = true;
                select.appendChild(opt);
            });
        }

        return select;
    }

    createCheckbox(field) {
        const container = document.createElement('div');
        container.className = 'form-check';

        const input = document.createElement('input');
        input.type = 'checkbox';
        input.name = field.name;
        input.id = field.name;
        input.className = 'form-check-input';
        input.value = field.value || '1';
        
        if (field.checked) input.checked = true;

        const label = document.createElement('label');
        label.className = 'form-check-label';
        label.setAttribute('for', field.name);
        label.textContent = field.checkboxLabel || field.label;

        container.appendChild(input);
        container.appendChild(label);

        return container;
    }

    createRadio(field) {
        const container = document.createElement('div');
        
        if (field.options) {
            field.options.forEach(option => {
                const radioContainer = document.createElement('div');
                radioContainer.className = 'form-check';

                const input = document.createElement('input');
                input.type = 'radio';
                input.name = field.name;
                input.id = `${field.name}_${option.value}`;
                input.className = 'form-check-input';
                input.value = option.value;
                
                if (option.value === field.value) input.checked = true;

                const label = document.createElement('label');
                label.className = 'form-check-label';
                label.setAttribute('for', `${field.name}_${option.value}`);
                label.textContent = option.label;

                radioContainer.appendChild(input);
                radioContainer.appendChild(label);
                container.appendChild(radioContainer);
            });
        }

        return container;
    }

    createFileInput(field) {
        const input = document.createElement('input');
        input.type = 'file';
        input.name = field.name;
        input.id = field.name;
        input.className = 'form-control';
        
        if (field.multiple) input.multiple = true;
        if (field.accept) input.accept = field.accept;

        return input;
    }

    getFormData() {
        const formData = new FormData(this.element);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        return data;
    }

    setData(data) {
        Object.keys(data).forEach(key => {
            const field = this.element.querySelector(`[name="${key}"]`);
            if (field) {
                if (field.type === 'checkbox') {
                    field.checked = !!data[key];
                } else {
                    field.value = data[key] || '';
                }
            }
        });
        return this;
    }

    validate() {
        return this.element.checkValidity();
    }

    reset() {
        this.element.reset();
        return this;
    }
}

// ==========================================================================
// ГРАФИК
// ==========================================================================

class ChartComponent extends BaseComponent {
    get defaultOptions() {
        return {
            type: 'line',
            data: {},
            options: {},
            responsive: true
        };
    }

    render() {
        const container = document.createElement('div');
        container.className = 'chart-container';

        const canvas = document.createElement('canvas');
        container.appendChild(canvas);

        return container;
    }

    afterMount() {
        const canvas = this.element.querySelector('canvas');
        this.chart = new Chart(canvas, {
            type: this.options.type,
            data: this.options.data,
            options: {
                responsive: this.options.responsive,
                ...this.options.options
            }
        });
    }

    updateData(data) {
        if (this.chart) {
            this.chart.data = data;
            this.chart.update();
        }
        return this;
    }

    destroy() {
        if (this.chart) {
            this.chart.destroy();
        }
        super.destroy();
    }
}

// ==========================================================================
// КАРТА
// ==========================================================================

class MapComponent extends BaseComponent {
    get defaultOptions() {
        return {
            center: [55.7558, 37.6176], // Москва
            zoom: 10,
            tiles: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            attribution: '© OpenStreetMap contributors'
        };
    }

    render() {
        const container = document.createElement('div');
        container.className = 'map-container';
        container.style.height = this.options.height || '400px';
        
        return container;
    }

    afterMount() {
        this.map = L.map(this.element).setView(this.options.center, this.options.zoom);
        
        L.tileLayer(this.options.tiles, {
            attribution: this.options.attribution
        }).addTo(this.map);

        this.emit('ready', this.map);
    }

    addMarker(lat, lng, options = {}) {
        const marker = L.marker([lat, lng], options).addTo(this.map);
        this.emit('markerAdded', marker);
        return marker;
    }

    setView(lat, lng, zoom) {
        if (this.map) {
            this.map.setView([lat, lng], zoom || this.options.zoom);
        }
        return this;
    }

    destroy() {
        if (this.map) {
            this.map.remove();
        }
        super.destroy();
    }
}

// ==========================================================================
// ЗАГРУЗКА ФАЙЛОВ
// ==========================================================================

class FileUploadComponent extends BaseComponent {
    get defaultOptions() {
        return {
            multiple: true,
            accept: '*/*',
            maxSize: 10 * 1024 * 1024, // 10MB
            dragDrop: true,
            preview: true
        };
    }

    render() {
        const container = document.createElement('div');
        container.className = 'file-upload-component';

        if (this.options.dragDrop) {
            const dropzone = document.createElement('div');
            dropzone.className = 'custom-file-upload';
            dropzone.innerHTML = `
                <i class="bi-cloud-upload display-1 text-muted"></i>
                <p>Перетащите файлы сюда или нажмите для выбора</p>
                <input type="file" class="d-none" ${this.options.multiple ? 'multiple' : ''} accept="${this.options.accept}">
            `;

            dropzone.addEventListener('click', () => {
                dropzone.querySelector('input').click();
            });

            container.appendChild(dropzone);
        }

        if (this.options.preview) {
            const preview = document.createElement('div');
            preview.className = 'file-preview mt-3';
            container.appendChild(preview);
        }

        return container;
    }

    afterMount() {
        const input = this.element.querySelector('input[type="file"]');
        if (input) {
            input.addEventListener('change', (e) => {
                this.handleFiles(e.target.files);
            });
        }

        if (this.options.dragDrop) {
            this.setupDragDrop();
        }
    }

    setupDragDrop() {
        const dropzone = this.element.querySelector('.custom-file-upload');
        
        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('dragover');
        });

        dropzone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            dropzone.classList.remove('dragover');
        });

        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.classList.remove('dragover');
            this.handleFiles(e.dataTransfer.files);
        });
    }

    handleFiles(files) {
        const validFiles = Array.from(files).filter(file => {
            if (file.size > this.options.maxSize) {
                console.warn(`File ${file.name} is too large`);
                return false;
            }
            return true;
        });

        this.emit('files', validFiles);

        if (this.options.preview) {
            this.showPreview(validFiles);
        }
    }

    showPreview(files) {
        const preview = this.element.querySelector('.file-preview');
        if (!preview) return;

        preview.innerHTML = '';

        files.forEach(file => {
            const item = document.createElement('div');
            item.className = 'file-preview-item d-flex align-items-center p-2 border rounded mb-2';
            item.innerHTML = `
                <i class="bi-file-earmark me-2"></i>
                <span class="flex-grow-1">${file.name}</span>
                <small class="text-muted">${this.formatFileSize(file.size)}</small>
            `;
            preview.appendChild(item);
        });
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// ==========================================================================
// ЭКСПОРТ
// ==========================================================================

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        ComponentManager,
        BaseComponent,
        ModalComponent,
        TableComponent,
        FormComponent,
        ChartComponent,
        MapComponent,
        FileUploadComponent
    };
} else {
    window.ComponentManager = ComponentManager;
    window.components = {
        ComponentManager,
        BaseComponent,
        ModalComponent,
        TableComponent,
        FormComponent,
        ChartComponent,
        MapComponent,
        FileUploadComponent
    };
}
