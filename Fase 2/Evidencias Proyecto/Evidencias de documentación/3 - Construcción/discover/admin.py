from django.contrib import admin

# Register your models here.

from .models import Usuario, Empresa, Administrador, TipoRecomendacion, Genero, EstadoAprobacion, Recomendacion, \
RecomendacionGuardada, MeGusta, Reporte, GestionUsuario, GestionEmpresa, AprobacionRecomendacion

admin.site.register(Usuario)
admin.site.register(Empresa)
admin.site.register(Administrador)
admin.site.register(TipoRecomendacion)
admin.site.register(Genero)
admin.site.register(EstadoAprobacion)
admin.site.register(Recomendacion)
admin.site.register(RecomendacionGuardada)
admin.site.register(MeGusta)
admin.site.register(Reporte)
admin.site.register(GestionUsuario)
admin.site.register(GestionEmpresa)
admin.site.register(AprobacionRecomendacion)
