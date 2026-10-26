from rest_framework.routers import DefaultRouter
from discover.api.views import UsuarioViewSet, EmpresaViewSet, RecomendacionViewSet, MeGustaViewSet

router_usuarios = DefaultRouter()
router_empresas = DefaultRouter()
router_recomendacion = DefaultRouter()
router_megusta = DefaultRouter()

router_usuarios.register(prefix = 'usuario', viewset = UsuarioViewSet, basename ='usuario')
router_empresas.register(prefix = 'empresa', viewset = EmpresaViewSet, basename = 'empresa')
router_recomendacion.register(prefix = 'recomendacion', viewset = RecomendacionViewSet, basename = 'recomendacion')
router_megusta.register(r'megusta', MeGustaViewSet, basename='megusta')
