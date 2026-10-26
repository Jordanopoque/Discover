from django.urls import path
from .views import UsuarioCreateAPIView
from discover.api.views import login_usuario_api
from . import views

urlpatterns = [
    path('usuarios/', UsuarioCreateAPIView.as_view(), name='usuario-create'),
    path('empresas/', EmpresaCreateAPIView.as_view(), name='empresa-create'),
    path('api/login/', login_usuario_api, name='login_usuario_api'),
    path('api/generos/', views.obtener_generos, name='obtener_generos'),
    path('recomendacionesrecomendacion/', obtener_recomendaciones),
]