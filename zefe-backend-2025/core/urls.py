
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path,include
from django.urls import path, re_path
from .swagger import schema_view  # or wherever you placed the schema_view
from catalog.views import telegram_webhook

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/',include('user.urls')),
    path('api/v1/',include('events.urls')),
    path('api/v1/',include('catalog.urls')),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('telegram/webhook/', telegram_webhook, name='telegram_webhook'),

]
# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

1