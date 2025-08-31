/**
 * Service Worker для PWA функциональности
 * Электронный журнал производства работ
 */

const CACHE_NAME = 'electronic-journal-v1.0.0';
const urlsToCache = [
    '/',
    '/index.html',
    '/login.html',
    '/css/main.css',
    '/js/main.js',
    '/js/api.js',
    '/js/auth.js',
    '/js/components.js',
    '/images/logo.png',
    '/images/default-avatar.png',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
    'https://cdn.jsdelivr.net/npm/chart.js@4.0.0/dist/chart.min.js',
    'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',
    'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',
    'https://cdn.socket.io/4.7.2/socket.io.min.js'
];

// Установка Service Worker
self.addEventListener('install', event => {
    console.log('Service Worker installing...');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('Opened cache');
                return cache.addAll(urlsToCache);
            })
            .catch(error => {
                console.error('Failed to cache resources:', error);
            })
    );
});

// Активация Service Worker
self.addEventListener('activate', event => {
    console.log('Service Worker activating...');
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

// Обработка fetch запросов
self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                // Возвращаем кешированную версию если есть
                if (response) {
                    return response;
                }

                // Клонируем запрос
                const fetchRequest = event.request.clone();

                return fetch(fetchRequest).then(response => {
                    // Проверяем валидность ответа
                    if (!response || response.status !== 200 || response.type !== 'basic') {
                        return response;
                    }

                    // Клонируем ответ для кеширования
                    const responseToCache = response.clone();

                    caches.open(CACHE_NAME)
                        .then(cache => {
                            cache.put(event.request, responseToCache);
                        });

                    return response;
                }).catch(() => {
                    // Возвращаем офлайн страницу для навигационных запросов
                    if (event.request.destination === 'document') {
                        return caches.match('/offline.html');
                    }
                });
            })
    );
});

// Push уведомления
self.addEventListener('push', event => {
    console.log('Push message received:', event);
    
    let notificationData = {};
    
    if (event.data) {
        try {
            notificationData = event.data.json();
        } catch (error) {
            console.error('Error parsing push data:', error);
            notificationData = {
                title: 'Новое уведомление',
                body: event.data.text() || 'У вас есть новое уведомление'
            };
        }
    }

    const options = {
        body: notificationData.body || 'Новое уведомление в журнале',
        icon: '/images/notification-icon.png',
        badge: '/images/badge-icon.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: notificationData.id || 1,
            url: notificationData.url || '/'
        },
        actions: [
            {
                action: 'explore',
                title: 'Открыть',
                icon: '/images/checkmark.png'
            },
            {
                action: 'close',
                title: 'Закрыть',
                icon: '/images/xmark.png'
            }
        ],
        requireInteraction: true
    };

    event.waitUntil(
        self.registration.showNotification(
            notificationData.title || 'Электронный журнал',
            options
        )
    );
});

// Обработка кликов по уведомлениям
self.addEventListener('notificationclick', event => {
    console.log('Notification click received:', event);

    event.notification.close();

    if (event.action === 'explore') {
        // Открываем приложение
        event.waitUntil(
            clients.openWindow(event.notification.data.url || '/')
        );
    } else if (event.action === 'close') {
        // Просто закрываем уведомление
        return;
    } else {
        // Клик по самому уведомлению
        event.waitUntil(
            clients.matchAll().then(clientList => {
                if (clientList.length > 0) {
                    // Фокусируемся на существующей вкладке
                    return clientList[0].focus();
                }
                // Открываем новую вкладку
                return clients.openWindow('/');
            })
        );
    }
});

// Фоновая синхронизация
self.addEventListener('sync', event => {
    console.log('Background sync:', event);
    
    if (event.tag === 'background-sync') {
        event.waitUntil(doBackgroundSync());
    }
});

async function doBackgroundSync() {
    try {
        // Получаем данные из IndexedDB для синхронизации
        const pendingData = await getPendingData();
        
        for (const item of pendingData) {
            try {
                await syncDataItem(item);
                await removePendingDataItem(item.id);
            } catch (error) {
                console.error('Failed to sync item:', item, error);
            }
        }
    } catch (error) {
        console.error('Background sync failed:', error);
    }
}

async function getPendingData() {
    // Заглушка для получения данных из IndexedDB
    return [];
}

async function syncDataItem(item) {
    // Заглушка для синхронизации элемента
    console.log('Syncing item:', item);
}

async function removePendingDataItem(id) {
    // Заглушка для удаления синхронизированного элемента
    console.log('Removing synced item:', id);
}

// Обработка сообщений от главного потока
self.addEventListener('message', event => {
    console.log('Service Worker received message:', event.data);
    
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    if (event.data && event.data.type === 'GET_VERSION') {
        event.ports[0].postMessage({ version: CACHE_NAME });
    }
});
