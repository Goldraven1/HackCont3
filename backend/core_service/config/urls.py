"""
URL configuration for Journal System project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework.documentation import include_docs_urls

# Create a router and register our viewsets with it
router = DefaultRouter()

# API v1 URLs
api_v1_patterns = [
    path('auth/', include('apps.users.urls')),
    path('projects/', include('apps.projects.urls')),
    path('journal/', include('apps.journal.urls')),
    path('documents/', include('apps.documents.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('reports/', include('apps.reports.urls')),
    path('', include(router.urls)),
]

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API
    path('api/v1/', include(api_v1_patterns)),
    path('api-auth/', include('rest_framework.urls')),
    
    # API Documentation
    path('api/docs/', include_docs_urls(title='Journal System API')),
    
    # Health check
    path('health/', include('apps.common.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns

# Custom error handlers
handler400 = 'apps.common.views.bad_request'
handler403 = 'apps.common.views.permission_denied'
handler404 = 'apps.common.views.page_not_found'
handler500 = 'apps.common.views.server_error'
