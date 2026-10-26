from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from discover.models import Usuario, Empresa, Recomendacion, MeGusta, TipoRecomendacion, Genero, EstadoAprobacion, RecomendacionGuardada

class UsuarioSerializer(ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'correo', 'contrasena', 'p_nombre', 'p_apellido', 'foto_perfil', 'fecha_registro'] #Datos que va a devolver el serializer
        extra_kwargs = {
            'contrasena': {'write_only': True}  # No mostrar en respuestas
        }
        
class EmpresaSerializer(ModelSerializer):
    class Meta:
        model = Empresa
        fields = ['id', 'correo', 'contrasena', 'nombre_empresa', 'foto_perfil', 'fecha_registro']
        extra_kwargs = {
            'contrasena': {'write_only': True}
        }

class RecomendacionSerializer(serializers.ModelSerializer):
    total_guardados = serializers.IntegerField(read_only=True)
    fecha_guardado = serializers.DateTimeField(read_only=True)
    estado_aprobacion = serializers.PrimaryKeyRelatedField(read_only=True)
    tipo_nombre = serializers.SerializerMethodField()
    genero_nombre = serializers.SerializerMethodField()
    
    tipo = serializers.PrimaryKeyRelatedField(queryset=TipoRecomendacion.objects.all())
    genero = serializers.PrimaryKeyRelatedField(queryset=Genero.objects.all())
    usuario = serializers.PrimaryKeyRelatedField(read_only=True)
    empresa = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Recomendacion
        fields = '__all__'

    def get_tipo_nombre(self, obj):
        return str(obj.tipo)

    def get_genero_nombre(self, obj):
        return obj.genero.nombre

class RecomendacionGuardadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecomendacionGuardada
        fields = '__all__'

class MeGustaSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.SerializerMethodField()
    usuario = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = MeGusta
        fields = ['id', 'recomendacion', 'usuario', 'usuario_nombre']

    def get_usuario_nombre(self, obj):
        return f"{obj.usuario.p_nombre} {obj.usuario.p_apellido}"