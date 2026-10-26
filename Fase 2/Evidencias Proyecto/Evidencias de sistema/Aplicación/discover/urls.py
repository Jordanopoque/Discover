from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

from discover.api.router import router_usuarios, router_empresas, router_recomendacion

urlpatterns = [
    # URLs públicas
    path('', views.landing_page, name='landing_page'),
    path('home/', views.home, name='inicio'),
    path('login/', views.login, name='login'),
    path('registro/', views.registro, name='registro'),
    path('registro_empresa/', views.registro_empresa, name='registro_empresa'),
    path('home/', views.home, name="home"),
    path('set-category-filter/', views.set_category_filter, name='set_category_filter'),
    path('principal/', views.principal, name='principal'),
    path('crear-recomendacion/', views.crear_recomendacion, name='crear_recomendacion'),
    path('generar-recomendacion-ia/', views.generar_recomendacion_ia, name='generar_recomendacion_ia'),
    path('generar-audio-recomendacion/', views.generar_audio_recomendacion, name='generar_audio_recomendacion'),
    path('obtener-generos/', views.obtener_generos_por_tipo, name='obtener_generos_por_tipo'),
    path('perfil/', views.perfil, name='perfil'),
    path('guardar-recomendacion/', views.guardar_recomendacion, name='guardar_recomendacion'),
    path('gustar-recomendacion/', views.gustar_recomendacion, name='gustar_recomendacion'),
    path('reportar-recomendacion/<int:recomendacion_id>/', views.reportar_recomendacion, name='reportar_recomendacion'),
    path('eliminar-recomendacion/', views.eliminar_recomendacion, name='eliminar_recomendacion'),
    path('recomendacion/<int:recomendacion_id>/', views.detalle_recomendacion_coleccion, name='detalle_recomendacion'),
    path('detalle-recomendacion-admin/<int:recomendacion_id>/', views.detalle_recomendacion_admin, name='detalle_recomendacion_admin'),
    path('coleccion/', views.coleccion, name='coleccion'),
    path('eliminar-cuenta/<str:tipo>/', views.eliminar_cuenta, name='eliminar_cuenta'),
    path('logout/', views.logout, name='logout'),
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('password-reset-confirm/<str:token>/', views.password_reset_confirm, name='password_reset_confirm'),

    # URLs de administración
    path('admin-panel/', views.panel_administrador, name='panel_administrador'),
    path('admin-panel/administracion/', views.panel_administrativo, name='panel_administrativo'),
    path('admin-panel/session-activity/', views.estado_sesiones_admin, name='admin_session_activity_status'),
    path('admin-panel/gestion-recomendaciones/', views.gestion_recomendaciones, name='gestion_recomendaciones'),
    path('admin-panel/aprobar-recomendacion/<int:recomendacion_id>/', views.aprobar_recomendacion, name='aprobar_recomendacion'),
    path('admin-panel/rechazar-recomendacion/<int:recomendacion_id>/', views.rechazar_recomendacion, name='rechazar_recomendacion'),
    
    # Gestión de usuarios
    path('admin-panel/gestion-usuarios/', views.gestion_usuarios, name='gestion_usuarios'),
    path('admin-panel/bloquear-usuario/<int:usuario_id>/', views.bloquear_usuario, name='bloquear_usuario'),
    path('admin-panel/desbloquear-usuario/<int:usuario_id>/', views.desbloquear_usuario, name='desbloquear_usuario'),
    path('admin-panel/desactivar-usuario/<int:usuario_id>/', views.desactivar_usuario, name='desactivar_usuario'),
    path('admin-panel/reactivar-usuario/<int:usuario_id>/', views.reactivar_usuario, name='reactivar_usuario'),
    path('admin-panel/eliminar-usuario/<int:usuario_id>/', views.eliminar_usuario, name='eliminar_usuario'),
    
    # Gestión de empresas
    path('admin-panel/gestion-empresas/', views.gestion_empresas, name='gestion_empresas'),
    path('admin-panel/bloquear-empresa/<int:empresa_id>/', views.bloquear_empresa, name='bloquear_empresa'),
    path('admin-panel/desbloquear-empresa/<int:empresa_id>/', views.desbloquear_empresa, name='desbloquear_empresa'),
    path('admin-panel/desactivar-empresa/<int:empresa_id>/', views.desactivar_empresa, name='desactivar_empresa'),
    path('admin-panel/reactivar-empresa/<int:empresa_id>/', views.reactivar_empresa, name='reactivar_empresa'),
    path('admin-panel/eliminar-empresa/<int:empresa_id>/', views.eliminar_empresa, name='eliminar_empresa'),

    # Gestión de categorías
    path('admin-panel/gestion-categorias/', views.gestion_categorias, name='gestion_categorias'),
    path('admin-panel/agregar-tipo/', views.agregar_tipo, name='agregar_tipo'),
    path('admin-panel/eliminar-tipo/<int:tipo_id>/', views.eliminar_tipo, name='eliminar_tipo'),
    path('admin-panel/agregar-genero/', views.agregar_genero, name='agregar_genero'),
    path('admin-panel/eliminar-genero/<int:genero_id>/', views.eliminar_genero, name='eliminar_genero'),

    path('admin-panel/gestion-reportes/', views.gestion_reportes, name='gestion_reportes'),
    path('admin-panel/reporte/<int:reporte_id>/', views.detalle_reporte, name='detalle_reporte'),
    path('admin-panel/reporte/<int:reporte_id>/cambiar-estado/', views.cambiar_estado_reporte, name='cambiar_estado_reporte'),

    path('mis-recomendaciones/usuario/', views.recomendaciones_subidas_usuario, name='recomendaciones_subidas_usuario'),
    path('mis-recomendaciones/empresa/', views.recomendaciones_subidas_empresa, name='recomendaciones_subidas_empresa'),
    path('mis-recomendaciones/detalle/<int:recomendacion_id>/', views.detalle_recomendacion_subida, name='detalle_recomendacion_subida'),
    

    # APIs / Endpoints
    path('api/usuarios', include(router_usuarios.urls)), #URL para la api de usuarios
    path('api/empresas', include(router_empresas.urls)), #URL para la api de empresas
    path('api/recomendaciones', include(router_recomendacion.urls)), #URL para la api de recomendaciones
]