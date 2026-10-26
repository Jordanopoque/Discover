"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from discover.api import views as api_views
from django.conf import settings
from django.conf.urls.static import static

from discover.api.router import router_usuarios, router_empresas, router_megusta

from discover.api.views import login_usuario_api, obtener_recomendaciones, guardar_recomendacion, gustar_recomendacion, recomendaciones_guardadas, crear_reporte, password_reset_request_api, password_reset_confirm, recomendaciones_guardadas_todas, csrf_token_api, session_api, logout_api

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('discover.urls')), #URL para las vistas de la app discover
    path('api/login/', login_usuario_api, name='login_usuario_api'),
    path('api/csrf/', csrf_token_api, name='csrf_token_api'),
    path('api/session/', session_api, name='session_api'),
    path('api/logout/', logout_api, name='logout_api'),
    path('api/generos/', api_views.obtener_generos, name='obtener_generos'),
    path('api/tipos/', api_views.obtener_tipos, name='obtener_tipos'),
    path('recomendacionesrecomendacion/', obtener_recomendaciones, name='obtener_recomendaciones'),
    path('api/', include(router_megusta.urls)),
    path('api/guardar_recomendacion/', guardar_recomendacion, name='guardar_recomendacion'),
    path('api/gustar_recomendacion/', gustar_recomendacion, name='gustar_recomendacion'),
    path('api/recomendaciones_guardadas/', recomendaciones_guardadas, name='recomendaciones_guardadas'),
    path('api/crear_reporte/', crear_reporte, name='crear_reporte'),
    path('api/password-reset-request/', password_reset_request_api, name='password-reset-request-api'),
    path('password-reset-confirm/', password_reset_confirm, name='password_reset_confirm'),
    path('api/recomendaciones_guardadas_todas/', recomendaciones_guardadas_todas, name='recomendaciones_guardadas_todas'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) #Código necesario para poder ver las imagenes en el navegador