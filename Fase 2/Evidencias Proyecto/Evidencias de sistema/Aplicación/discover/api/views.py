import json
from rest_framework import generics
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.viewsets import ModelViewSet
from discover.models import Usuario, Empresa, Administrador, Recomendacion, Genero, MeGusta, RecomendacionGuardada, EstadoAprobacion, Reporte, TipoRecomendacion
from discover.api.serializers import UsuarioSerializer, EmpresaSerializer, RecomendacionSerializer, MeGustaSerializer
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail


from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.hashers import check_password

from django.utils.decorators import method_decorator

from rest_framework.views import APIView

from django.http import JsonResponse

from django.shortcuts import get_object_or_404

from rest_framework.exceptions import ValidationError
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from discover.authentication import enforce_discover_csrf, get_discover_session_principal
from discover.session_activity import end_session_activity, start_session_activity


@ensure_csrf_cookie
@api_view(['GET'])
@permission_classes([AllowAny])
def csrf_token_api(request):
    return Response({'csrfToken': get_token(request)})


@api_view(['GET'])
@permission_classes([AllowAny])
def session_api(request):
    principal = get_discover_session_principal(request.session)
    if principal is None:
        return Response({'authenticated': False, 'user_id': None, 'user_type': None})
    return Response({
        'authenticated': True,
        'user_id': principal.id,
        'user_type': principal.user_type,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def logout_api(request):
    enforce_discover_csrf(request)
    end_session_activity(request)
    request.session.flush()
    return Response({'authenticated': False})


class UsuarioViewSet(ModelViewSet):
    serializer_class = UsuarioSerializer

    def get_permissions(self):
        permission = AllowAny if self.action == 'create' else IsAuthenticated
        return [permission()]

    def get_queryset(self):
        if self.action == 'create':
            return Usuario.objects.none()
        if self.request.user.user_type != 'usuario':
            return Usuario.objects.none()
        return Usuario.objects.filter(pk=self.request.user.id)

class EmpresaViewSet(ModelViewSet):
    serializer_class = EmpresaSerializer

    def get_permissions(self):
        permission = AllowAny if self.action == 'create' else IsAuthenticated
        return [permission()]

    def get_queryset(self):
        if self.action == 'create':
            return Empresa.objects.none()
        if self.request.user.user_type != 'empresa':
            return Empresa.objects.none()
        return Empresa.objects.filter(pk=self.request.user.id)

class RecomendacionViewSet(ModelViewSet):
    serializer_class = RecomendacionSerializer

    def get_permissions(self):
        permission = AllowAny if self.action in ('list', 'retrieve') else IsAuthenticated
        return [permission()]

    def get_queryset(self):
        queryset = Recomendacion.objects.filter(estado_aprobacion=1)

        if self.action not in ('list', 'retrieve'):
            if self.request.user.user_type == 'usuario':
                queryset = queryset.filter(usuario_id=self.request.user.id)
            elif self.request.user.user_type == 'empresa':
                queryset = queryset.filter(empresa_id=self.request.user.id)
            else:
                return Recomendacion.objects.none()

        usuario_id = self.request.query_params.get('usuario')
        tipo_id = self.request.query_params.get('tipo')

        if usuario_id is not None and self.action in ('list', 'retrieve'):
            try:
                usuario_id = int(usuario_id)
                queryset = queryset.filter(usuario_id=usuario_id)
            except ValueError:
                queryset = Recomendacion.objects.none()

        if tipo_id is not None:
            try:
                tipo_id = int(tipo_id)
                queryset = queryset.filter(tipo_id=tipo_id)
            except ValueError:
                queryset = Recomendacion.objects.none()

        return queryset

    def perform_create(self, serializer):
        estado = get_object_or_404(EstadoAprobacion, pk=2)
        principal = self.request.user
        if principal.user_type == 'usuario':
            serializer.save(
                estado_aprobacion=estado,
                usuario=principal.account,
                empresa=None,
            )
        elif principal.user_type == 'empresa':
            serializer.save(
                estado_aprobacion=estado,
                usuario=None,
                empresa=principal.account,
            )
        else:
            raise ValidationError({"detail": "Este tipo de cuenta no puede crear recomendaciones."})


class MeGustaViewSet(ModelViewSet):
    serializer_class = MeGustaSerializer

    def get_queryset(self):
        if self.action == 'list':
            return MeGusta.objects.all()
        if self.request.user.user_type != 'usuario':
            return MeGusta.objects.none()
        return MeGusta.objects.filter(usuario_id=self.request.user.id)

    def perform_create(self, serializer):
        if self.request.user.user_type != 'usuario':
            raise ValidationError({"detail": "Solo los usuarios pueden dar me gusta."})
        serializer.save(usuario=self.request.user.account)


class UsuarioCreateAPIView(APIView):
    def post(self, request):
        serializer = UsuarioSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'mensaje': '¡Registro exitoso!'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EmpresaCreateAPIView(APIView):
    def post(self, request):
        serializer = EmpresaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'mensaje': '¡Registro de empresa exitoso!'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class UsuarioCreateAPIView(generics.CreateAPIView):
#     queryset = Usuario.objects.all()
#     serializer_class = UsuarioSerializer
#     parser_classes = [MultiPartParser, FormParser]  # Necesario para recibir FormData

# views.py con Django REST Framework
from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['GET'])
@permission_classes([AllowAny])
def lista_tipos_api(request):
    tipos = UsuarioSerializer.objects.all()
    serializer = UsuarioSerializer(tipos, many=True)
    return Response(serializer.data)



@api_view(['POST'])
@permission_classes([AllowAny])
def login_usuario_api(request):
    enforce_discover_csrf(request)
    correo = request.data.get('correo')
    contrasena = request.data.get('contrasena')
    tipo_usuario = request.data.get('tipo_usuario')  # 👈 Nuevo campo

    if not correo or not contrasena or not tipo_usuario:
        return Response({'error': 'Correo, contraseña y tipo de usuario son obligatorios'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        if tipo_usuario == 'usuario':
            usuario = Usuario.objects.get(correo=correo)
            if check_password(contrasena, usuario.contrasena) and usuario.is_active and not usuario.is_blocked:
                request.session.flush()
                request.session['user_id'] = usuario.id
                request.session['user_type'] = 'usuario'
                request.session.set_expiry(0)
                start_session_activity(request)
                return Response({
                    'mensaje': 'Login exitoso',
                    'usuario_id': usuario.id,
                    'tipo_usuario': 'usuario'
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Contraseña incorrecta'}, status=status.HTTP_401_UNAUTHORIZED)

        elif tipo_usuario == 'empresa':
            empresa = Empresa.objects.get(correo=correo)
            if check_password(contrasena, empresa.contrasena) and empresa.is_active and not empresa.is_blocked:
                request.session.flush()
                request.session['user_id'] = empresa.id
                request.session['user_type'] = 'empresa'
                request.session.set_expiry(0)
                start_session_activity(request)
                return Response({
                    'mensaje': 'Login exitoso',
                    'empresa_id': empresa.id,
                    'tipo_usuario': 'empresa'
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Contraseña incorrecta'}, status=status.HTTP_401_UNAUTHORIZED)

        elif tipo_usuario == 'administrador':
            admin = Administrador.objects.get(correo=correo)
            if check_password(contrasena, admin.contrasena):
                request.session.flush()
                request.session['user_id'] = admin.id
                request.session['user_type'] = 'administrador'
                request.session.set_expiry(0)
                start_session_activity(request)
                return Response({
                    'mensaje': 'Login exitoso',
                    'usuario_id': admin.id,
                    'tipo_usuario': 'administrador'
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Contraseña incorrecta'}, status=status.HTTP_401_UNAUTHORIZED)
        
        else:
            return Response({'error': 'Tipo de usuario no válido'}, status=status.HTTP_400_BAD_REQUEST)

    except (Usuario.DoesNotExist, Empresa.DoesNotExist, Administrador.DoesNotExist):
        return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

# def obtener_generos(request):
#     tipo_id = request.GET.get('tipo_id')
#     if tipo_id:
#         generos = Genero.objects.filter(tipo_recomendacion_id=tipo_id).values('id', 'nombre')
#         return JsonResponse(list(generos), safe=False)
#    return JsonResponse([], safe=False)

@api_view(['GET'])
@permission_classes([AllowAny])
def obtener_generos(request):
    tipo = request.query_params.get('tipo')

    if tipo:
        generos = Genero.objects.filter(tipo_recomendacion_id=tipo)
    else:
        generos = Genero.objects.all().distinct()

    generos_obj = [{'id': g.id, 'nombre': g.nombre} for g in generos]

    return Response(generos_obj)


@api_view(['GET'])
@permission_classes([AllowAny])
def obtener_tipos(request):
    tipos = TipoRecomendacion.objects.all().values('id', 'nombre')
    return Response(list(tipos))


@api_view(['GET'])
def obtener_recomendaciones(request):
    principal = request.user
    if principal.user_type == 'usuario':
        queryset = Recomendacion.objects.filter(usuario_id=principal.id)
    elif principal.user_type == 'empresa':
        queryset = Recomendacion.objects.filter(empresa_id=principal.id)
    else:
        queryset = Recomendacion.objects.none()

    serializer = RecomendacionSerializer(queryset, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def guardar_recomendacion(request):
    if request.user.user_type != 'usuario':
        raise ValidationError({"detail": "Solo los usuarios pueden guardar recomendaciones."})
    recomendacion_id = request.data.get('recomendacion_id')
    if not recomendacion_id:
        return Response({'status': 'error', 'message': 'Falta recomendacion_id'}, status=400)
    guardada, created = RecomendacionGuardada.objects.get_or_create(
        usuario=request.user.account,
        recomendacion_id=recomendacion_id,
    )
    if not created:
        guardada.delete()
    return Response({
        'status': 'success',
        'message': 'Recomendación guardada' if created else 'Recomendación eliminada',
        'bookmarked': created,
    })


@api_view(['POST'])
def gustar_recomendacion(request):
    if request.user.user_type != 'usuario':
        raise ValidationError({"detail": "Solo los usuarios pueden dar me gusta."})
    recomendacion_id = request.data.get('recomendacion_id')
    if not recomendacion_id:
        return Response({'status': 'error', 'message': 'Falta recomendacion_id'}, status=400)
    megusta, created = MeGusta.objects.get_or_create(
        usuario=request.user.account,
        recomendacion_id=recomendacion_id,
    )
    if not created:
        megusta.delete()
    return Response({
        'status': 'success',
        'message': 'Me gusta agregado' if created else 'Me gusta eliminado',
        'liked': created,
    })

@api_view(['GET'])
def recomendaciones_guardadas(request):
    if request.user.user_type != 'usuario':
        raise ValidationError({"detail": "Solo los usuarios pueden consultar su colección."})

    try:
        guardadas = RecomendacionGuardada.objects.filter(usuario_id=request.user.id)

        recomendaciones = []
        for g in guardadas:
            recomendacion = g.recomendacion

            # Total guardados
            total_guardados = RecomendacionGuardada.objects.filter(recomendacion=recomendacion).count()
            setattr(recomendacion, 'total_guardados', total_guardados)

            # Agregar fecha_guardado desde la relación intermedia
            setattr(recomendacion, 'fecha_guardado', g.fecha_guardado)

            recomendaciones.append(recomendacion)

        serializer = RecomendacionSerializer(recomendaciones, many=True)
        return Response(serializer.data)

    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
def recomendaciones_guardadas_todas(request):
    guardados = RecomendacionGuardada.objects.values('recomendacion_id')
    return Response([
        {'recomendacion': guardado['recomendacion_id']}
        for guardado in guardados
    ])


@api_view(['POST'])
def crear_reporte(request):
    if request.user.user_type != 'usuario':
        raise ValidationError({"detail": "Solo los usuarios pueden reportar recomendaciones."})
    motivo = request.data.get('motivo', '').strip()
    recomendacion_id = request.data.get('recomendacion')
    if not motivo or not recomendacion_id:
        return Response({'error': 'Recomendación y motivo son requeridos.'}, status=400)
    Reporte.objects.create(
        usuario=request.user.account,
        recomendacion=get_object_or_404(Recomendacion, pk=recomendacion_id),
        motivo=motivo,
    )
    return Response({'message': 'Reporte creado correctamente.'}, status=201)

@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request_api(request):
    correo = request.data.get('correo')
    tipo_usuario = request.data.get('tipo_usuario')

    if not correo or not tipo_usuario:
        return Response({'message': 'Correo y tipo_usuario son requeridos'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        if tipo_usuario == 'usuario':
            user = Usuario.objects.get(correo=correo)
        else:
            user = Empresa.objects.get(correo=correo)
    except (Usuario.DoesNotExist, Empresa.DoesNotExist):
        return Response({'message': 'No existe una cuenta con ese correo'}, status=status.HTTP_404_NOT_FOUND)

    # Generar token
    token = user.generate_reset_token()

    # Obtener URL base dinámica
    scheme = request.scheme
    host = request.get_host()
    reset_url = f'{scheme}://{host}/password-reset-confirm/{token}/'

    # Enviar correo
    send_mail(
        'Recuperación de contraseña - Discover',
        f'Para restablecer tu contraseña, visita: {reset_url}',
        'no-reply@discover.com',
        [correo],
        fail_silently=False,
    )

    return Response({'message': 'Se ha enviado un correo con instrucciones'}, status=status.HTTP_200_OK)


@csrf_exempt
def password_reset_confirm(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        token = data.get('token')
        nueva_contrasena = data.get('nueva_contrasena')

        user = Usuario.get_user_by_token(token)
        if not user:
            return JsonResponse({'error': 'Token inválido o expirado'}, status=400)
        
        user.contrasena = nueva_contrasena  # Esto llamará a save() que la has hasheado
        user.reset_token = None
        user.reset_token_expires = None
        user.save()

        return JsonResponse({'message': 'Contraseña restablecida correctamente'})