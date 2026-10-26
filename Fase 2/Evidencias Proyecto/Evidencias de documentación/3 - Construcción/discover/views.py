import base64
import hashlib
import random
import json
import logging
import os
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.cache import cache
from django.views.decorators.http import require_POST
from discover.authentication import get_discover_session_principal
from discover.analytics import (
    build_admin_dashboard_context,
    get_admin_session_activity_snapshot,
)
from discover.session_activity import end_session_activity, start_session_activity
from django.utils import timezone
from multiprocessing import context
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from discover.models import Usuario, Empresa, Recomendacion, TipoRecomendacion, Genero, RecomendacionGuardada, MeGusta, Reporte, Administrador, GestionUsuario, GestionEmpresa, AprobacionRecomendacion    
from django.views.decorators.http import require_POST
from .forms import RegistroUsuarioForm, RegistroEmpresaForm, LoginForm, RecomendacionForm, EditarEmpresaForm, EditarUsuarioForm, PasswordResetRequestForm, PasswordResetForm
from django.contrib import messages
from django.urls import reverse
from django.db.models.functions import Random
from .models import EstadoAprobacion
from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import send_mail

from django.contrib.sessions.models import SessionManager
# Create your views here.

from functools import wraps
from django.shortcuts import redirect

logger = logging.getLogger(__name__)

def landing_page(request):
    return render(request, 'discover/landing.html')

def login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        principal = get_discover_session_principal(request.session)
        if principal is None:
            request.session.flush()
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        principal = get_discover_session_principal(request.session)
        if principal is None:
            request.session.flush()
            messages.error(request, "Acceso no autorizado")
            return redirect('login')
        if principal.user_type != 'administrador':
            messages.error(request, "Acceso no autorizado")
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
    
@login_required
def home(request):
    if 'user_id' not in request.session:
        return redirect('login')

    

    tipos_recomendacion = TipoRecomendacion.objects.exclude(nombre="Promocional")
    context = {
        'tipos_recomendacion': tipos_recomendacion,
        'request': request
    }

    try:
        if request.session['user_type'] == 'usuario':
            usuario = Usuario.objects.get(id=request.session['user_id'])
            context['usuario'] = usuario
        elif request.session['user_type'] == 'empresa':
            empresa = Empresa.objects.get(id=request.session['user_id'])
            context['empresa'] = empresa
    except (Usuario.DoesNotExist, Empresa.DoesNotExist):
        messages.error(request, "Sesión inválida")
        return redirect('login')

    return render(request, 'discover/home.html', context)


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data['correo']
            contrasena = form.cleaned_data['contrasena']
            tipo_usuario = form.cleaned_data['tipo_usuario']

            if not correo or not contrasena or not tipo_usuario:
                messages.error(request, 'Todos los campos son obligatorios')
                return redirect('discover/login.html')
            
            try:
                if tipo_usuario == 'usuario':
                    usuario = Usuario.objects.get(correo=correo)
                    if not usuario.is_active:
                        messages.error(request, "Esta cuenta ha sido desactivada")
                        return redirect('login')
                    if usuario.is_blocked:
                        messages.error(request, f"Cuenta bloqueada. Razón: {usuario.blocked_reason}")
                        return redirect('login')
                    if usuario.check_password(contrasena):
                        request.session.flush()
                        request.session['user_id'] = usuario.id
                        request.session['user_type'] = 'usuario'
                        start_session_activity(request)
                        return redirect('home')
                    else:
                        messages.error(request, "Contraseña incorrecta")
                elif tipo_usuario == 'empresa':
                    empresa = Empresa.objects.get(correo=correo)
                    if not empresa.is_active:
                        messages.error(request, "Esta cuenta ha sido desactivada")
                        return redirect('login')
                    if empresa.is_blocked:
                        messages.error(request, f"Cuenta bloqueada. Razón: {empresa.blocked_reason}")
                        return redirect('login')
                    if empresa.check_password(contrasena):
                        request.session.flush()
                        request.session['user_id'] = empresa.id
                        request.session['user_type'] = 'empresa'
                        start_session_activity(request)
                        return redirect('home')
                    else:
                        messages.error(request, "Contraseña incorrecta")
                elif tipo_usuario == 'administrador':
                    admin = Administrador.objects.get(correo=correo)
                    if admin.check_password(contrasena):
                        request.session.flush()
                        request.session['user_id'] = admin.id
                        request.session['user_type'] = 'administrador'
                        start_session_activity(request)
                        return redirect('panel_administrador')
                    else:
                        messages.error(request, "Contraseña incorrecta")
            except Exception as e:
                messages.error(request, "Credenciales inválidas")
                print(f"Error en login: {str(e)}")
    else:
        form = LoginForm()
    
    return render(request, 'discover/login.html', {'form': form})

@login_required
def principal(request):
    if 'user_id' not in request.session:
        return redirect('login')
    
    # Manejar el filtro de categoría (tu código existente)
    if request.method == 'POST':
        categoria_id = request.POST.get('categoria_filtro')
        if categoria_id:
            request.session['categoria_filtro'] = int(categoria_id)
            # Resetear al cambiar categoría
            if 'recomendaciones_vistas' in request.session:
                del request.session['recomendaciones_vistas']
        elif 'categoria_filtro' in request.session:
            del request.session['categoria_filtro']
            if 'recomendaciones_vistas' in request.session:
                del request.session['recomendaciones_vistas']
    
    context = {}
    
    try:
        if request.session['user_type'] == 'usuario':
            usuario = Usuario.objects.get(id=request.session['user_id'])
            context['usuario'] = usuario
        elif request.session['user_type'] == 'empresa':
            empresa = Empresa.objects.get(id=request.session['user_id'])
            context['empresa'] = empresa
    except (Usuario.DoesNotExist, Empresa.DoesNotExist):
        messages.error(request, "Sesión inválida")
        return redirect('login')
    
    # Obtener recomendaciones aprobadas (tu código existente)
    estado_aprobado = EstadoAprobacion.objects.get(nombre='aprobado')
    recomendaciones = Recomendacion.objects.filter(
        estado_aprobacion=estado_aprobado
    )
    
    # Aplicar filtro si existe (tu código existente)
    if 'categoria_filtro' in request.session:
        recomendaciones = recomendaciones.filter(tipo_id=request.session['categoria_filtro'])
    
    # Lógica nueva para evitar repeticiones:
    ids_disponibles = list(recomendaciones.values_list('id', flat=True))
    recomendaciones_vistas = request.session.get('recomendaciones_vistas', [])
    
    # Filtrar no vistas
    ids_no_vistas = [id for id in ids_disponibles if id not in recomendaciones_vistas]
    
    # Reiniciar ciclo si es necesario
    reiniciar = False
    if not ids_no_vistas and ids_disponibles:
        ids_no_vistas = ids_disponibles
        recomendaciones_vistas = []
        reiniciar = True
    
    # Seleccionar recomendación
    if ids_no_vistas:
        recomendacion_id = random.choice(ids_no_vistas)
        recomendacion = recomendaciones.get(id=recomendacion_id)
        recomendaciones_vistas.append(recomendacion_id)
        request.session['recomendaciones_vistas'] = recomendaciones_vistas
    else:
        recomendacion = None
    
    # Tu código existente para likes/bookmarks
    if 'user_id' in request.session and request.session['user_type'] == 'usuario':
        usuario_id = request.session['user_id']
        megustas_usuario = MeGusta.objects.filter(
            usuario_id=usuario_id
        ).values_list('recomendacion_id', flat=True)
        
        bookmarks_usuario = RecomendacionGuardada.objects.filter(
            usuario_id=usuario_id
        ).values_list('recomendacion_id', flat=True)
        
        context['megustas_usuario'] = list(megustas_usuario)
        context['bookmarks_usuario'] = list(bookmarks_usuario)
    else:
        context['megustas_usuario'] = []
        context['bookmarks_usuario'] = []
    
    # Añadir al contexto
    context.update({
        'recomendacion': recomendacion,
        'reiniciar': reiniciar,
        'recomendaciones': [recomendacion] if recomendacion else []  # Mantiene compatibilidad
    })
    
    return render(request, 'discover/principal.html', context)

from django.shortcuts import redirect
from django.contrib.auth import logout as auth_logout

@require_POST
def logout(request):
    end_session_activity(request)
    auth_logout(request)  # Esto limpia la sesión
    return redirect('login')  # Redirige a la página de login


def registro(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Registro exitoso! Por favor inicia sesión.')
            return redirect('login')
    else:
        form = RegistroUsuarioForm()
    
    return render(request, 'discover/registro.html', {'form': form})


def registro_empresa(request):
    if request.method == 'POST':
        form = RegistroEmpresaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Registro de empresa exitoso!')
            return redirect('login')
    else:
        form = RegistroEmpresaForm()
    
    return render(request, 'discover/registro_empresa.html', {'form': form})


@login_required
def crear_recomendacion(request):
    # Verificar autenticación
    if not request.session.get('user_id'):
        messages.error(request, "Debes iniciar sesión para crear recomendaciones")
        return redirect('login')
    
    # Obtener el usuario/empresa/administrador actual
    try:
        if request.session['user_type'] == 'usuario':
            creador = Usuario.objects.get(id=request.session['user_id'])
        elif request.session['user_type'] == 'empresa':
            creador = Empresa.objects.get(id=request.session['user_id'])
        elif request.session['user_type'] == 'administrador':
            creador = Administrador.objects.get(id=request.session['user_id'])
    except Exception as e:
        messages.error(request, "Usuario no encontrado")
        return redirect('principal')

    if request.method == 'POST':
        form = RecomendacionForm(request.POST, request.FILES, user_type=request.session.get('user_type'))
        if form.is_valid():
            try:
                recomendacion = form.save(commit=False)
                
                # Asignar creador según tipo
                if request.session['user_type'] == 'usuario':
                    recomendacion.usuario = creador
                    estado = EstadoAprobacion.objects.get(nombre='pendiente')
                elif request.session['user_type'] == 'empresa':
                    recomendacion.empresa = creador
                    estado = EstadoAprobacion.objects.get(nombre='pendiente')
                else:  # administrador
                    recomendacion.administrador = creador
                    estado = EstadoAprobacion.objects.get(nombre='aprobado')
                
                recomendacion.estado_aprobacion = estado
                recomendacion.save()
            
                messages.success(request, '¡Recomendación enviada con éxito!')
                return redirect('crear_recomendacion')
            
            except Exception as e:
                messages.error(request, f"Error al guardar: {str(e)}")
                print(f"Error en crear_recomendacion: {str(e)}")
        else:
            messages.error(request, "Por favor corrige los errores en el formulario")
    else:
        form = RecomendacionForm(user_type=request.session.get('user_type'))
    
    return render(request, 'discover/crear_recomendacion.html', {
        'form': form,
        'es_empresa': request.session.get('user_type') == 'empresa',
        'es_admin': request.session.get('user_type') == 'administrador'
    })


@login_required
@require_POST
def generar_recomendacion_ia(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'error': 'La solicitud no contiene datos válidos.'}, status=400)

    titulo = data.get('titulo') if isinstance(data, dict) else None
    if not isinstance(titulo, str) or not titulo.strip() or len(titulo.strip()) > 255:
        return JsonResponse({'error': 'Ingresa un título válido (máximo 255 caracteres).'}, status=400)

    api_key = os.environ.get('GEMINI_API_KEY', '').strip()
    if not api_key:
        return JsonResponse({
            'error': 'La generación con Gemini no está configurada. Contacta al administrador.'
        }, status=503)

    prompt = (
        'Genera en español el contenido para una recomendación de la obra indicada. '
        'Devuelve un resumen atractivo de 2 o 3 oraciones que invite a descubrirla, '
        'una trivia breve e interesante y una frase destacada original y memorable. '
        'Evita inventar hechos concretos en el resumen o la trivia si no los conoces. '
        'Completa los tres campos con texto útil y conciso.\n\n'
        f'Título: {titulo.strip()}'
    )
    payload = json.dumps({
        'contents': [{'parts': [{'text': prompt}]}],
        'generationConfig': {
            'temperature': 0.7,
            'maxOutputTokens': 450,
            'responseMimeType': 'application/json',
            'responseSchema': {
                'type': 'OBJECT',
                'properties': {
                    'resumen': {'type': 'STRING'},
                    'trivia': {'type': 'STRING'},
                    'frase_destacada': {'type': 'STRING'},
                },
                'required': ['resumen', 'trivia', 'frase_destacada'],
            },
        },
    }).encode('utf-8')
    model = settings.GEMINI_MODEL
    if not model:
        return JsonResponse({
            'error': 'El modelo de Gemini no está configurado. Contacta al administrador.'
        }, status=503)

    gemini_request = Request(
        f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',
        data=payload,
        headers={
            'Content-Type': 'application/json',
            'x-goog-api-key': api_key,
        },
        method='POST',
    )

    try:
        with urlopen(gemini_request, timeout=20) as response:
            gemini_response = json.loads(response.read())
    except HTTPError as error:
        error_body = error.read().decode('utf-8', errors='replace')
        logger.error(
            'Gemini API respondió con HTTP %s: %s',
            error.code,
            error_body[:1000],
        )
        if error.code == 404:
            models_request = Request(
                'https://generativelanguage.googleapis.com/v1beta/models',
                headers={'x-goog-api-key': api_key},
            )
            try:
                with urlopen(models_request, timeout=20) as response:
                    models_response = json.loads(response.read())
            except HTTPError as models_error:
                logger.error(
                    'No se pudieron consultar los modelos disponibles de Gemini (HTTP %s).',
                    models_error.code,
                )
                return JsonResponse({
                    'error': (
                        'No se pudo identificar un modelo disponible en Gemini. '
                        'Revisa la clave y los permisos de la API.'
                    )
                }, status=502)
            except (OSError, json.JSONDecodeError, UnicodeDecodeError):
                logger.exception('No se pudieron consultar los modelos disponibles de Gemini.')
                return JsonResponse({
                    'error': 'No se pudo consultar los modelos disponibles de Gemini.'
                }, status=502)

            available_models = models_response.get('models', []) if isinstance(models_response, dict) else []
            supported_models = [
                model_info['name'].removeprefix('models/')
                for model_info in available_models
                if isinstance(model_info, dict)
                and isinstance(model_info.get('name'), str)
                and 'generateContent' in model_info.get('supportedGenerationMethods', [])
                and model_info['name'].removeprefix('models/') != model
            ] if isinstance(available_models, list) else []
            model_priority = (
                'gemini-3.5-flash-lite',
                'gemini-2.5-flash',
                'gemini-2.5-flash-lite',
                'gemini-2.5-pro',
            )
            fallback_model = next(
                (candidate for candidate in model_priority if candidate in supported_models),
                next(iter(supported_models), None),
            )
            if not fallback_model:
                logger.error('La clave de Gemini no tiene modelos compatibles con generateContent.')
                return JsonResponse({
                    'error': (
                        'La clave de Gemini no tiene modelos disponibles para generar contenido.'
                    )
                }, status=502)

            logger.warning(
                'El modelo Gemini %s no está disponible; se reintentará con %s.',
                model,
                fallback_model,
            )
            fallback_request = Request(
                'https://generativelanguage.googleapis.com/v1beta/models/'
                f'{fallback_model}:generateContent',
                data=payload,
                headers={
                    'Content-Type': 'application/json',
                    'x-goog-api-key': api_key,
                },
                method='POST',
            )
            try:
                with urlopen(fallback_request, timeout=20) as response:
                    gemini_response = json.loads(response.read())
            except HTTPError as fallback_error:
                logger.error(
                    'El modelo alternativo de Gemini %s respondió con HTTP %s: %s',
                    fallback_model,
                    fallback_error.code,
                    fallback_error.read().decode('utf-8', errors='replace')[:1000],
                )
                return JsonResponse({
                    'error': (
                        'Gemini no pudo generar el contenido con los modelos disponibles. '
                        'Revisa los detalles en el log del servidor.'
                    )
                }, status=502)
            except (OSError, json.JSONDecodeError, UnicodeDecodeError):
                logger.exception('No se pudo generar contenido con el modelo alternativo Gemini.')
                return JsonResponse({
                    'error': 'No se pudo generar el contenido con Gemini. Inténtalo nuevamente.'
                }, status=502)
        else:
            return JsonResponse({
                'error': f'Gemini rechazó la solicitud (HTTP {error.code}). Revisa la configuración de la API.'
            }, status=502)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        logger.exception('No se pudo generar el contenido con Gemini.')
        return JsonResponse({
            'error': 'No se pudo generar el contenido. Inténtalo nuevamente más tarde.'
        }, status=502)

    candidates = gemini_response.get('candidates', []) if isinstance(gemini_response, dict) else []
    if not isinstance(candidates, list) or not candidates or not isinstance(candidates[0], dict):
        logger.error('Gemini respondió sin candidatos para generar contenido.')
        return JsonResponse({
            'error': 'Gemini no pudo generar contenido para este título.'
        }, status=502)

    content = candidates[0].get('content')
    parts = content.get('parts', []) if isinstance(content, dict) else []
    generated_text = ' '.join(
        part['text']
        for part in parts
        if isinstance(part, dict) and isinstance(part.get('text'), str)
    ).strip() if isinstance(parts, list) else ''
    try:
        generated_content = json.loads(generated_text)
    except json.JSONDecodeError:
        generated_content = None

    required_fields = ('resumen', 'trivia', 'frase_destacada')
    if (
        not isinstance(generated_content, dict)
        or any(
            not isinstance(generated_content.get(field), str)
            or not generated_content[field].strip()
            for field in required_fields
        )
    ):
        logger.error('Gemini respondió con contenido incompleto o inválido.')
        return JsonResponse({
            'error': 'Gemini no pudo generar los tres textos para este título.'
        }, status=502)

    return JsonResponse({
        field: generated_content[field].strip()
        for field in required_fields
    })


@require_POST
def generar_audio_recomendacion(request):
    if get_discover_session_principal(request.session) is None:
        return JsonResponse({'error': 'Inicia sesión para reproducir el audio.'}, status=401)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'error': 'La solicitud no contiene datos válidos.'}, status=400)

    if not isinstance(data, dict):
        return JsonResponse({'error': 'La solicitud no contiene datos válidos.'}, status=400)

    recomendacion_id = data.get('recomendacion_id')
    section = data.get('section')
    section_fields = {
        'resumen': 'resumen',
        'trivia': 'trivia',
        'frase_destacada': 'frase_destacada',
    }
    if (
        not isinstance(recomendacion_id, int)
        or isinstance(recomendacion_id, bool)
        or not isinstance(section, str)
        or section not in section_fields
    ):
        return JsonResponse({'error': 'La sección solicitada no es válida.'}, status=400)

    try:
        recomendacion = Recomendacion.objects.get(id=recomendacion_id)
    except Recomendacion.DoesNotExist:
        return JsonResponse({'error': 'La recomendación solicitada no existe.'}, status=404)

    text = getattr(recomendacion, section_fields[section])
    if not isinstance(text, str) or not text.strip():
        return JsonResponse({'error': 'Esta sección no tiene texto para reproducir.'}, status=400)
    if len(text) > 10000:
        return JsonResponse({'error': 'El texto de esta sección supera el máximo permitido.'}, status=400)

    model = getattr(settings, 'GEMINI_TTS_MODEL', '').strip()
    api_key = os.environ.get('GEMINI_API_KEY', '').strip()
    if not model or not api_key:
        logger.error('La generación TTS de Gemini no está configurada.')
        return JsonResponse({
            'error': 'El audio con Gemini no está configurado. Contacta al administrador.'
        }, status=503)

    cache_digest = hashlib.sha256(
        f'{model}\0Kore\0{section}\0{text}'.encode('utf-8')
    ).hexdigest()
    cache_key = f'gemini-tts-v1:{cache_digest}'
    cached_audio = cache.get(cache_key)
    if cached_audio is not None:
        return HttpResponse(cached_audio, content_type='audio/wav')

    payload = json.dumps({
        'model': model,
        'input': [{
            'type': 'user_input',
            'content': [{
                'type': 'text',
                'text': text,
                'annotations': [{
                    'type': 'speech_metadata',
                    'style': (
                        'Read the supplied Spanish text verbatim, without adding, '
                        'summarizing, translating, or omitting any words.'
                    ),
                }],
            }],
        }],
        'response_format': {'type': 'audio'},
        'generation_config': {
            'speech_config': [{'voice': 'Kore'}],
        },
    }).encode('utf-8')
    gemini_request = Request(
        'https://generativelanguage.googleapis.com/v1beta/interactions',
        data=payload,
        headers={
            'Content-Type': 'application/json',
            'x-goog-api-key': api_key,
        },
        method='POST',
    )

    try:
        with urlopen(gemini_request, timeout=45) as response:
            gemini_response = json.loads(response.read())
    except HTTPError as error:
        error_body = error.read().decode('utf-8', errors='replace')
        logger.error(
            'Gemini TTS API respondió con HTTP %s: %s',
            error.code,
            error_body[:1000],
        )
        return JsonResponse({
            'error': 'Gemini no pudo generar el audio. Inténtalo nuevamente más tarde.'
        }, status=502)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        logger.exception('No se pudo generar audio con Gemini.')
        return JsonResponse({
            'error': 'No se pudo generar el audio. Inténtalo nuevamente más tarde.'
        }, status=502)

    steps = gemini_response.get('steps', []) if isinstance(gemini_response, dict) else []
    audio_base64 = None
    if isinstance(steps, list):
        for step in reversed(steps):
            if not isinstance(step, dict) or step.get('type') != 'model_output':
                continue
            content = step.get('content', [])
            if not isinstance(content, list):
                continue
            for part in reversed(content):
                if (
                    isinstance(part, dict)
                    and part.get('type') == 'audio'
                    and isinstance(part.get('data'), str)
                ):
                    audio_base64 = part['data']
                    break
            if audio_base64:
                break

    try:
        audio_bytes = base64.b64decode(audio_base64, validate=True)
    except (TypeError, ValueError):
        logger.error('Gemini TTS respondió sin audio WAV válido.')
        return JsonResponse({
            'error': 'Gemini no devolvió un audio reproducible. Inténtalo nuevamente.'
        }, status=502)

    if len(audio_bytes) < 12 or audio_bytes[:4] != b'RIFF' or audio_bytes[8:12] != b'WAVE':
        logger.error('Gemini TTS respondió con un formato de audio inesperado.')
        return JsonResponse({
            'error': 'Gemini no devolvió un audio reproducible. Inténtalo nuevamente.'
        }, status=502)

    cache.set(cache_key, audio_bytes, timeout=60 * 60 * 24)
    return HttpResponse(audio_bytes, content_type='audio/wav')


@login_required
def perfil(request):
    context = {}
    
    try:
        if request.session['user_type'] == 'usuario':
            usuario = Usuario.objects.get(id=request.session['user_id'])
            
            if request.method == 'POST':
                form = EditarUsuarioForm(request.POST, request.FILES, instance=usuario)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Perfil actualizado correctamente')
                    return redirect('perfil')
            else:
                form = EditarUsuarioForm(instance=usuario)
            
            context['form'] = form
            context['usuario'] = usuario
            template = 'discover/perfil_usuario.html'
            
        elif request.session['user_type'] == 'empresa':
            empresa = Empresa.objects.get(id=request.session['user_id'])
            
            if request.method == 'POST':
                form = EditarEmpresaForm(request.POST, request.FILES, instance=empresa)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Perfil de empresa actualizado correctamente')
                    return redirect('perfil')
            else:
                form = EditarEmpresaForm(instance=empresa)
            
            context['form'] = form
            context['empresa'] = empresa
            template = 'discover/perfil_empresa.html'
            
        else:
            messages.error(request, "Tipo de usuario no válido")
            return redirect('principal')
    
    except (Usuario.DoesNotExist, Empresa.DoesNotExist):
        messages.error(request, "Sesión inválida")
        return redirect('login')
    
    return render(request, template, context)



def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data['correo']
            tipo_usuario = form.cleaned_data['tipo_usuario']
            
            try:
                if tipo_usuario == 'usuario':
                    user = Usuario.objects.get(correo=correo)
                else:
                    user = Empresa.objects.get(correo=correo)
                
                token = user.generate_reset_token()
                
                # Enviar correo
                reset_url = request.build_absolute_uri(
                    f'/password-reset-confirm/{token}/'
                )
                
                send_mail(
                    'Recuperación de contraseña - Discover',
                    f'Para restablecer tu contraseña, visita: {reset_url}',
                    'no-reply@discover.com',
                    [correo],
                    fail_silently=False,
                )
                
                messages.success(request, 'Se ha enviado un correo con instrucciones')
                return redirect('login')
                
            except (Usuario.DoesNotExist, Empresa.DoesNotExist):
                messages.error(request, 'No existe una cuenta con ese correo')
    else:
        form = PasswordResetRequestForm()
    
    return render(request, 'discover/password_reset_request.html', {'form': form})

def password_reset_confirm(request, token):
    # Buscar usuario o empresa con el token válido
    user = None
    try:
        user = Usuario.objects.get(reset_token=token)
    except Usuario.DoesNotExist:
        try:
            user = Empresa.objects.get(reset_token=token)
        except Empresa.DoesNotExist:
            pass
    
    if not user or not user.is_reset_token_valid():
        messages.error(request, 'Enlace inválido o expirado')
        return redirect('login')
    
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            # Actualizar contraseña
            user.contrasena = make_password(form.cleaned_data['nueva_contrasena'])
            user.reset_token = None
            user.reset_token_expires = None
            user.save()
            
            messages.success(request, 'Contraseña actualizada correctamente')
            messages.success(request, 'Inicia sesión')
            return redirect('login')
    else:
        form = PasswordResetForm()
    
    return render(request, 'discover/password_reset_confirm.html', {
        'form': form,
        'validlink': True
    })

@login_required
def coleccion(request):
    context = {}
    try:
        # Obtener solo las recomendaciones del usuario actual con select_related para optimizar
        coleccion = RecomendacionGuardada.objects.filter(
            usuario_id=request.session['user_id']
        ).select_related('recomendacion')
        
        context['coleccion'] = coleccion
    except Exception as e:
        messages.error(request, f'Error al cargar la colección: {str(e)}')
    
    return render(request, 'discover/coleccion.html', context)


from django.http import JsonResponse

@login_required
def gustar_recomendacion(request):
    if request.method == 'POST':
        if request.session.get('user_type') != 'usuario':
            return JsonResponse({'status': 'error', 'message': 'Solo usuarios pueden dar me gusta'}, status=403)
        try:
            recomendacion_id = request.POST.get('recomendacion_id')
            usuario_id = request.session.get('user_id')
            
            # Verificar si ya existe
            megusta, created = MeGusta.objects.get_or_create(
                usuario_id=usuario_id,
                recomendacion_id=recomendacion_id
            )
            
            if not created:
                # Si ya existía, lo eliminamos (toggle off)
                megusta.delete()
                return JsonResponse({
                    'status': 'success', 
                    'message': 'Me gusta eliminado',
                    'liked': False
                })
            
            return JsonResponse({
                'status': 'success', 
                'message': 'Me gusta agregado',
                'liked': True
            })
                
        except Exception as e:
            return JsonResponse({
                'status': 'error', 
                'message': str(e)
            }, status=500)
    
    return JsonResponse({
        'status': 'error', 
        'message': 'Método no permitido'
    }, status=405)

@login_required
def guardar_recomendacion(request):
    if request.method == 'POST':
        if request.session.get('user_type') != 'usuario':
            return JsonResponse({'status': 'error', 'message': 'Solo usuarios pueden guardar recomendaciones'}, status=403)
        try:
            recomendacion_id = request.POST.get('recomendacion_id')
            usuario_id = request.session.get('user_id')
            
            # Verificar si ya existe
            guardada, created = RecomendacionGuardada.objects.get_or_create(
                usuario_id=usuario_id,
                recomendacion_id=recomendacion_id
            )
            
            if not created:
                # Si ya existía, lo eliminamos (toggle off)
                guardada.delete()
                return JsonResponse({
                    'status': 'success', 
                    'message': 'Recomendación eliminada de guardados',
                    'bookmarked': False
                })
            
            return JsonResponse({
                'status': 'success', 
                'message': 'Recomendación guardada',
                'bookmarked': True
            })
                
        except Exception as e:
            return JsonResponse({
                'status': 'error', 
                'message': str(e)
            }, status=500)
    
    return JsonResponse({
        'status': 'error', 
        'message': 'Método no permitido'
    }, status=405)


@login_required
def eliminar_recomendacion(request):
    if request.method == 'POST':
        if request.session.get('user_type') != 'usuario':
            return JsonResponse({'status': 'error', 'message': 'Solo usuarios pueden modificar su colección'}, status=403)
        try:
            recomendacion_id = request.POST.get('recomendacion_id')
            usuario_id = request.session.get('user_id')
            
            # Verificar que existe antes de eliminar
            guardada = RecomendacionGuardada.objects.filter(
                usuario_id=usuario_id,
                recomendacion_id=recomendacion_id
            ).first()
            
            if guardada:
                guardada.delete()
                return JsonResponse({
                    'status': 'success', 
                    'message': 'Recomendación eliminada de tu colección'
                })
            else:
                return JsonResponse({
                    'status': 'error', 
                    'message': 'La recomendación no estaba en tu colección'
                }, status=404)
                
        except Exception as e:
            return JsonResponse({
                'status': 'error', 
                'message': str(e)
            }, status=500)
    
    return JsonResponse({
        'status': 'error', 
        'message': 'Método no permitido'
    }, status=405)


@login_required
def detalle_recomendacion_coleccion(request, recomendacion_id):
    try:
        recomendacion = Recomendacion.objects.get(id=recomendacion_id)
        context = {'recomendacion': recomendacion}
        
        # Verificar si está guardada en colección para marcar el bookmark
        if request.session.get('user_id'):
            context['esta_guardada'] = RecomendacionGuardada.objects.filter(
                usuario_id=request.session['user_id'],
                recomendacion_id=recomendacion_id
            ).exists()
            
        return render(request, 'discover/detalle_recomendacion_coleccion.html', context)
    except Recomendacion.DoesNotExist:
        messages.error(request, 'La recomendación no existe')
        return redirect('coleccion')

@login_required
def detalle_recomendacion_admin(request, recomendacion_id):
    try:
        recomendacion = Recomendacion.objects.get(id=recomendacion_id)

        # Analizar de dónde viene
        referer = request.META.get('HTTP_REFERER', '')
        from_param = request.GET.get('from', '')

        if from_param == 'reportes' or 'gestion-reportes' in referer:
            volver_a = reverse('gestion_reportes')
        else:
            volver_a = reverse('gestion_recomendaciones')

        context = {
            'recomendacion': recomendacion,
            'volver_a': volver_a,
        }
        return render(request, 'discover/detalle_recomendacion_admin.html', context)

    except Recomendacion.DoesNotExist:
        messages.error(request, 'La recomendación no existe')
        return redirect('coleccion')
    

@login_required
def eliminar_cuenta(request, tipo):
    if request.method == 'POST':
        try:
            if tipo != request.session.get('user_type') or tipo not in ('usuario', 'empresa'):
                return JsonResponse({'status': 'error', 'message': 'No puedes eliminar esta cuenta'}, status=403)
            user_id = request.session.get('user_id')
            
            if tipo == 'usuario':
                usuario = Usuario.objects.get(id=user_id)
                # Eliminar recomendaciones guardadas primero
                RecomendacionGuardada.objects.filter(usuario=usuario).delete()
                # Eliminar recomendaciones creadas (las desvinculamos en lugar de eliminar)
                Recomendacion.objects.filter(usuario=usuario).update(usuario=None)
                # Finalmente eliminar el usuario
                usuario.delete()
            elif tipo == 'empresa':
                empresa = Empresa.objects.get(id=user_id)
                # Eliminar recomendaciones asociadas
                Recomendacion.objects.filter(empresa=empresa).delete()
                # Finalmente eliminar la empresa
                empresa.delete()
            
            # Limpiar la sesión
            auth_logout(request)
            
            return JsonResponse({
                'status': 'success',
                'message': 'Cuenta eliminada correctamente'
            })
            
        except Exception as e:
            print(f"Error al eliminar cuenta: {str(e)}")  # Log para debugging
            return JsonResponse({
                'status': 'error',
                'message': 'Se eliminó la cuenta pero ocurrió un error en el proceso'
            }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Método no permitido'
    }, status=405)



from django.shortcuts import render, redirect, get_object_or_404

@login_required
def reportar_recomendacion(request, recomendacion_id):
    if request.session.get('user_type') != 'usuario':
        return JsonResponse({'error': 'Solo los usuarios pueden reportar recomendaciones'}, status=403)
    recomendacion = get_object_or_404(Recomendacion, id=recomendacion_id)
    
    if request.method == 'POST':
        motivo = request.POST.get('motivo', '').strip()
        
        if not motivo:
            messages.error(request, 'Debes indicar un motivo para el reporte.')
        else:
            # Obtener el usuario actual (ajusta según tu modelo de usuarios)
            usuario = Usuario.objects.get(id=request.session.get('user_id'))
            
            # Crear el reporte
            Reporte.objects.create(
                usuario=usuario,
                recomendacion=recomendacion,
                motivo=motivo
            )
            
            messages.success(request, 'Reporte enviado correctamente. Gracias por ayudarnos a mejorar.')
    
    return render(request, 'discover/reportar_recomendacion.html', {
        'recomendacion': recomendacion
    })


from django.http import JsonResponse
from .models import Genero

def obtener_generos_por_tipo(request):
    tipo_id = request.GET.get('tipo_id')
    if not tipo_id:
        return JsonResponse({'generos': []})

    # Versión corregida - asegúrate de que los nombres sean strings
    generos = Genero.objects.filter(tipo_recomendacion_id=tipo_id).values('id', 'nombre')
    
    # Debug: Ver qué se está enviando realmente
    print("Géneros encontrados:", list(generos))
    
    return JsonResponse(list(generos), safe=False)  # Mantén safe=False para compatibilidad


@admin_required
def panel_administrador(request):
    # Verificar que es administrador
    if request.session.get('user_type') != 'administrador':
        return redirect('principal')
    
    try:
        admin = Administrador.objects.get(id=request.session['user_id'])
    except Administrador.DoesNotExist:
        messages.error(request, "Acceso no autorizado")
        return redirect('login')
    
    context = build_admin_dashboard_context(request.GET)
    context.update({
        'admin': admin,
    })
    
    return render(request, 'discover/panel_administrador.html', context)


@admin_required
def panel_administrativo(request):
    try:
        admin = Administrador.objects.get(id=request.session['user_id'])
    except Administrador.DoesNotExist:
        messages.error(request, "Acceso no autorizado")
        return redirect('login')

    context = {
        'admin': admin,
        'pendientes': Recomendacion.objects.filter(
            estado_aprobacion__nombre='pendiente'
        ).count(),
        'usuarios': Usuario.objects.count(),
        'empresas': Empresa.objects.count(),
        'reportes_pendientes': Reporte.objects.filter(estado='pendiente').count(),
    }
    return render(request, 'discover/panel_administrativo.html', context)


def estado_sesiones_admin(request):
    principal = get_discover_session_principal(request.session)
    if principal is None or principal.user_type != 'administrador':
        return JsonResponse({'error': 'Acceso no autorizado'}, status=403)

    return JsonResponse({
        'sessions': get_admin_session_activity_snapshot(request.GET),
    })


@admin_required
def gestion_recomendaciones(request):
    if request.session.get('user_type') != 'administrador':
        return redirect('principal')
    
    estado = request.GET.get('estado', 'pendiente')
    
    recomendaciones = Recomendacion.objects.filter(
        estado_aprobacion__nombre=estado
    ).select_related('usuario', 'empresa', 'tipo', 'genero')
    
    estados = EstadoAprobacion.objects.all()
    
    context = {
        'recomendaciones': recomendaciones,
        'estados': estados,
        'estado_actual': estado
    }
    
    return render(request, 'discover/gestion_recomendaciones.html', context)

@admin_required
def aprobar_recomendacion(request, recomendacion_id):
    if request.session.get('user_type') != 'administrador':
        return redirect('principal')
    
    try:
        admin = Administrador.objects.get(id=request.session['user_id'])
        recomendacion = Recomendacion.objects.get(id=recomendacion_id)
        estado_aprobado = EstadoAprobacion.objects.get(nombre='aprobado')
        
        recomendacion.estado_aprobacion = estado_aprobado
        recomendacion.administrador = admin
        recomendacion.save()
        
        # Registrar la acción
        AprobacionRecomendacion.objects.create(
            administrador=admin,
            recomendacion=recomendacion,
            estado_aprobacion=estado_aprobado,
            comentario="Recomendación aprobada"
        )
        
        messages.success(request, 'Recomendación aprobada exitosamente')
    except Exception as e:
        messages.error(request, f'Error al aprobar recomendación: {str(e)}')
    
    return redirect('gestion_recomendaciones')

@admin_required
def rechazar_recomendacion(request, recomendacion_id):
    if request.method == 'POST' and request.session.get('user_type') == 'administrador':
        try:
            admin = Administrador.objects.get(id=request.session['user_id'])
            recomendacion = Recomendacion.objects.get(id=recomendacion_id)
            estado_rechazado = EstadoAprobacion.objects.get(nombre='rechazado')
            comentario = request.POST.get('comentario', '')
            
            recomendacion.estado_aprobacion = estado_rechazado
            recomendacion.administrador = admin
            recomendacion.save()
            
            # Registrar la acción
            AprobacionRecomendacion.objects.create(
                administrador=admin,
                recomendacion=recomendacion,
                estado_aprobacion=estado_rechazado,
                comentario=comentario
            )
            
            messages.success(request, 'Recomendación rechazada exitosamente')
        except Exception as e:
            messages.error(request, f'Error al rechazar recomendación: {str(e)}')
    
    return redirect('gestion_recomendaciones')

@admin_required
def gestion_usuarios(request):
    usuarios = Usuario.objects.all().order_by('-fecha_registro')
    usuarios_activos = Usuario.objects.filter(is_active=True, is_blocked=False).count()
    usuarios_bloqueados = Usuario.objects.filter(is_blocked=True).count()
    usuarios_inactivos = Usuario.objects.filter(is_active=False).count()
    
    return render(request, 'discover/gestion_usuarios.html', {
        'usuarios': usuarios,
        'usuarios_activos': usuarios_activos,
        'usuarios_bloqueados': usuarios_bloqueados,
        'usuarios_inactivos': usuarios_inactivos
    })

@admin_required
def gestion_empresas(request):
    empresas = Empresa.objects.all().order_by('-fecha_registro')
    empresas_activas = Empresa.objects.filter(is_active=True, is_blocked=False).count()
    empresas_bloqueadas = Empresa.objects.filter(is_blocked=True).count()
    empresas_inactivas = Empresa.objects.filter(is_active=False).count()
    
    return render(request, 'discover/gestion_empresas.html', {
        'empresas': empresas,
        'empresas_activas': empresas_activas,
        'empresas_bloqueadas': empresas_bloqueadas,
        'empresas_inactivas': empresas_inactivas
    })

@admin_required
def bloquear_usuario(request, usuario_id):
    if request.method == 'POST':
        try:
            admin = Administrador.objects.get(id=request.session['user_id'])
            usuario = Usuario.objects.get(id=usuario_id)
            motivo = request.POST.get('motivo', 'Violación de términos de servicio')
            
            # Actualizar campos de bloqueo
            usuario.is_blocked = True
            usuario.blocked_reason = motivo
            usuario.blocked_at = timezone.now()
            usuario.save()
            
            # Registrar acción
            GestionUsuario.objects.create(
                administrador=admin,
                usuario=usuario,
                accion='bloquear',
                detalle=motivo
            )
            
            messages.success(request, f'Usuario {usuario.correo} bloqueado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al bloquear usuario: {str(e)}')
    
    return redirect('gestion_usuarios')

@admin_required
def desbloquear_usuario(request, usuario_id):
    if request.method == 'POST':
        try:
            admin = Administrador.objects.get(id=request.session['user_id'])
            usuario = Usuario.objects.get(id=usuario_id)
            
            # Quitar bloqueo
            usuario.is_blocked = False
            usuario.blocked_reason = None
            usuario.blocked_at = None
            usuario.save()
            
            # Registrar acción
            GestionUsuario.objects.create(
                administrador=admin,
                usuario=usuario,
                accion='desbloquear'
            )
            
            messages.success(request, f'Usuario {usuario.correo} desbloqueado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al desbloquear usuario: {str(e)}')
    
    return redirect('gestion_usuarios')

@admin_required
def desactivar_usuario(request, usuario_id):
    if request.method == 'POST':
        try:
            admin = Administrador.objects.get(id=request.session['user_id'])
            usuario = Usuario.objects.get(id=usuario_id)
            
            # Desactivar cuenta
            usuario.is_active = False
            usuario.save()
            
            # Registrar acción
            GestionUsuario.objects.create(
                administrador=admin,
                usuario=usuario,
                accion='desactivar'
            )
            
            messages.success(request, f'Usuario {usuario.correo} desactivado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al desactivar usuario: {str(e)}')
    
    return redirect('gestion_usuarios')

@admin_required
def reactivar_usuario(request, usuario_id):
    if request.method == 'POST':
        try:
            admin = Administrador.objects.get(id=request.session['user_id'])
            usuario = Usuario.objects.get(id=usuario_id)
            
            # Reactivar cuenta
            usuario.is_active = True
            usuario.save()
            
            # Registrar acción
            GestionUsuario.objects.create(
                administrador=admin,
                usuario=usuario,
                accion='reactivar'
            )
            
            messages.success(request, f'Usuario {usuario.correo} reactivado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al reactivar usuario: {str(e)}')
    
    return redirect('gestion_usuarios')

@admin_required
def eliminar_usuario(request, usuario_id):
    if request.method == 'POST':
        try:
            admin = Administrador.objects.get(id=request.session['user_id'])
            usuario = Usuario.objects.get(id=usuario_id)
            
            # Eliminación lógica (recomendado)
            usuario.is_active = False
            usuario.save()
            
            # O eliminación física (si es necesario)
            # usuario.delete()
            
            # Registrar acción
            GestionUsuario.objects.create(
                administrador=admin,
                usuario=usuario,
                accion='eliminar'
            )
            
            messages.success(request, f'Usuario {usuario.correo} eliminado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al eliminar usuario: {str(e)}')
    
    return redirect('gestion_usuarios')

# Vistas similares para empresas (desactivar_empresa, reactivar_empresa, eliminar_empresa)

@admin_required
def bloquear_empresa(request, empresa_id):
    if request.method == 'POST':
        try:
            admin = Administrador.objects.get(id=request.session['user_id'])
            empresa = Empresa.objects.get(id=empresa_id)
            motivo = request.POST.get('motivo', 'Violación de términos de servicio')
            
            # Actualizar campos de bloqueo
            empresa.is_blocked = True
            empresa.blocked_reason = motivo
            empresa.blocked_at = timezone.now()
            empresa.save()
            
            # Registrar acción
            GestionEmpresa.objects.create(
                administrador=admin,
                empresa=empresa,
                accion='bloquear',
                detalle=motivo
            )
            
            messages.success(request, f'Empresa {empresa.correo} bloqueada exitosamente')
        except Exception as e:
            messages.error(request, f'Error al bloquear empresa: {str(e)}')
    
    return redirect('gestion_empresas')

@admin_required
def desbloquear_empresa(request, empresa_id):
    if request.method == 'POST':
        try:
            admin = Administrador.objects.get(id=request.session['user_id'])
            empresa = Empresa.objects.get(id=empresa_id)
            
            # Quitar bloqueo
            empresa.is_blocked = False
            empresa.blocked_reason = None
            empresa.blocked_at = None
            empresa.save()
            
            # Registrar acción
            GestionEmpresa.objects.create(
                administrador=admin,
                empresa=empresa,
                accion='desbloquear'
            )
            
            messages.success(request, f'Empresa {empresa.correo} desbloqueada exitosamente')
        except Exception as e:
            messages.error(request, f'Error al desbloquear empresa: {str(e)}')
    
    return redirect('gestion_empresas')

@admin_required
def desactivar_empresa(request, empresa_id):
    if request.method == 'POST':
        try:
            admin = Administrador.objects.get(id=request.session['user_id'])
            empresa = Empresa.objects.get(id=empresa_id)
            
            # Desactivar cuenta
            empresa.is_active = False
            empresa.save()
            
            # Registrar acción
            GestionEmpresa.objects.create(
                administrador=admin,
                empresa=empresa,
                accion='desactivar'
            )
            
            messages.success(request, f'Empresa {empresa.correo} desactivada exitosamente')
        except Exception as e:
            messages.error(request, f'Error al desactivar empresa: {str(e)}')
    
    return redirect('gestion_empresas')

@admin_required
def reactivar_empresa(request, empresa_id):
    if request.method == 'POST':
        try:
            admin = Administrador.objects.get(id=request.session['user_id'])
            empresa = Empresa.objects.get(id=empresa_id)
            
            # Reactivar cuenta
            empresa.is_active = True
            empresa.save()
            
            # Registrar acción
            GestionEmpresa.objects.create(
                administrador=admin,
                empresa=empresa,
                accion='reactivar'
            )
            
            messages.success(request, f'Empresa {empresa.correo} reactivada exitosamente')
        except Exception as e:
            messages.error(request, f'Error al reactivar empresa: {str(e)}')
    
    return redirect('gestion_empresas')

@admin_required
def eliminar_empresa(request, empresa_id):
    if request.method == 'POST':
        try:
            admin = Administrador.objects.get(id=request.session['user_id'])
            empresa = Empresa.objects.get(id=empresa_id)
            
            # Eliminación lógica (recomendado)
            empresa.is_active = False
            empresa.save()
            
            # O eliminación física (si es necesario)
            # empresa.delete()
            
            # Registrar acción
            GestionEmpresa.objects.create(
                administrador=admin,
                empresa=empresa,
                accion='eliminar'
            )
            
            messages.success(request, f'Empresa {empresa.correo} eliminada exitosamente')
        except Exception as e:
            messages.error(request, f'Error al eliminar empresa: {str(e)}')
    
    return redirect('gestion_empresas')


from .forms import TipoRecomendacionForm, GeneroForm
from django.views.decorators.http import require_POST

@admin_required
def gestion_categorias(request):
    tipos = TipoRecomendacion.objects.all().order_by('nombre')
    generos = Genero.objects.all().select_related('tipo_recomendacion').order_by('tipo_recomendacion__nombre', 'nombre')
    
    tipo_form = TipoRecomendacionForm()
    genero_form = GeneroForm()
    
    context = {
        'tipos': tipos,
        'generos': generos,
        'tipo_form': tipo_form,
        'genero_form': genero_form
    }
    return render(request, 'discover/gestion_categorias.html', context)

@require_POST
@admin_required
def agregar_tipo(request):
    form = TipoRecomendacionForm(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, 'Tipo de recomendación agregado exitosamente')
    else:
        messages.error(request, 'Error al agregar el tipo de recomendación')
    return redirect('gestion_categorias')

@require_POST
@admin_required
def eliminar_tipo(request, tipo_id):
    try:
        tipo = TipoRecomendacion.objects.get(id=tipo_id)
        tipo.delete()
        messages.success(request, 'Tipo de recomendación eliminado exitosamente')
    except TipoRecomendacion.DoesNotExist:
        messages.error(request, 'El tipo de recomendación no existe')
    except Exception as e:
        messages.error(request, f'Error al eliminar tipo: {str(e)}')
    return redirect('gestion_categorias')

@require_POST
@admin_required
def agregar_genero(request):
    form = GeneroForm(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, 'Género agregado exitosamente')
    else:
        messages.error(request, 'Error al agregar el género')
    return redirect('gestion_categorias')

@require_POST
@admin_required
def eliminar_genero(request, genero_id):
    try:
        genero = Genero.objects.get(id=genero_id)
        genero.delete()
        messages.success(request, 'Género eliminado exitosamente')
    except Genero.DoesNotExist:
        messages.error(request, 'El género no existe')
    except Exception as e:
        messages.error(request, f'Error al eliminar género: {str(e)}')
    return redirect('gestion_categorias')


from .forms import GestionReporteForm
from django.db.models import Count

@admin_required
def gestion_reportes(request):
    estado = request.GET.get('estado', 'pendiente')
    
    reportes = Reporte.objects.filter(estado=estado).select_related(
        'usuario', 'recomendacion', 'administrador'
    ).order_by('-fecha')
    
    # Estadísticas
    conteo_estados = Reporte.objects.values('estado').annotate(
        total=Count('id')
    ).order_by('estado')
    
    context = {
        'reportes': reportes,
        'estado_actual': estado,
        'conteo_estados': conteo_estados,
        'estados_disponibles': dict(Reporte.ESTADOS)
    }
    return render(request, 'discover/gestion_reportes.html', context)

@admin_required
def detalle_reporte(request, reporte_id):
    reporte = get_object_or_404(Reporte, id=reporte_id)
    
    if request.method == 'POST':
        form = GestionReporteForm(request.POST, instance=reporte)
        if form.is_valid():
            reporte = form.save(commit=False)
            reporte.administrador = Administrador.objects.get(id=request.session['user_id'])
            
            if form.cleaned_data['estado'] in ['resuelto', 'rechazado'] and not reporte.fecha_resolucion:
                reporte.fecha_resolucion = timezone.now()
            
            reporte.save()
            
            # Opcional: Notificar al usuario si el estado cambia
            if form.has_changed():
                messages.success(request, 'Reporte actualizado exitosamente')
            return redirect('detalle_reporte', reporte_id=reporte.id)
    else:
        form = GestionReporteForm(instance=reporte)
    
    context = {
        'reporte': reporte,
        'form': form
    }
    return render(request, 'discover/detalle_reporte.html', context)

@admin_required
@require_POST
def cambiar_estado_reporte(request, reporte_id):
    reporte = get_object_or_404(Reporte, id=reporte_id)
    nuevo_estado = request.POST.get('estado')
    
    if nuevo_estado in dict(Reporte.ESTADOS).keys():
        reporte.estado = nuevo_estado
        reporte.administrador = Administrador.objects.get(id=request.session['user_id'])
        
        if nuevo_estado in ['resuelto', 'rechazado']:
            reporte.fecha_resolucion = timezone.now()
        
        reporte.save()
        messages.success(request, f'Estado del reporte actualizado a {reporte.get_estado_display()}')
    else:
        messages.error(request, 'Estado no válido')
    
    return redirect('gestion_reportes')

from django.http import JsonResponse

@login_required
def set_category_filter(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            category_id = data.get('category_id')
            
            if category_id:
                request.session['categoria_filtro'] = int(category_id)
            else:
                if 'categoria_filtro' in request.session:
                    del request.session['categoria_filtro']
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
def recomendaciones_subidas_usuario(request):
    if request.session.get('user_type') != 'usuario':
        return redirect('principal')
    
    try:
        usuario = Usuario.objects.get(id=request.session['user_id'])
        recomendaciones = Recomendacion.objects.filter(usuario=usuario).order_by('-fecha_creacion')
        
        context = {
            'recomendaciones': recomendaciones,
            'usuario': usuario
        }
        
        return render(request, 'discover/recomendaciones_subidas_usuario.html', context)
    except Usuario.DoesNotExist:
        messages.error(request, "Usuario no encontrado")
        return redirect('principal')

@login_required
def recomendaciones_subidas_empresa(request):
    if request.session.get('user_type') != 'empresa':
        return redirect('principal')
    
    try:
        empresa = Empresa.objects.get(id=request.session['user_id'])
        # Obtener recomendaciones con conteo de likes
        recomendaciones = Recomendacion.objects.filter(
            empresa=empresa
        ).annotate(
            num_likes=Count('megusta')
        ).order_by('-fecha_creacion')
        
        context = {
            'recomendaciones': recomendaciones,
            'empresa': empresa
        }
        return render(request, 'discover/recomendaciones_subidas_empresa.html', context)
        
    except Empresa.DoesNotExist:
        messages.error(request, "Empresa no encontrada")
        return redirect('principal')

from django.db.models import Count
from django.shortcuts import render, redirect
from django.contrib import messages
from discover.models import Recomendacion, MeGusta

@login_required
def detalle_recomendacion_subida(request, recomendacion_id):
    try:
        # Obtener la recomendación con conteo de likes
        recomendacion = Recomendacion.objects.filter(
            id=recomendacion_id
        ).annotate(
            num_likes=Count('megusta')
        ).first()
        
        # Obtener los usuarios que dieron like (forma compatible con MySQL)
        usuarios_likes = []
        if recomendacion:
            usuarios_likes = list(MeGusta.objects.filter(
                recomendacion=recomendacion
            ).select_related('usuario').values_list(
                'usuario__correo',
                flat=True
            ))
        
        # Verificación de permisos
        user_id = request.session.get('user_id')
        user_type = request.session.get('user_type')
        
        if not recomendacion or (user_type == 'usuario' and recomendacion.usuario and recomendacion.usuario.id != user_id):
            messages.error(request, "No tienes permiso para ver esta recomendación")
            return redirect('principal')
        elif user_type == 'empresa' and recomendacion.empresa and recomendacion.empresa.id != user_id:
            messages.error(request, "No tienes permiso para ver esta recomendación")
            return redirect('principal')
        
        context = {
            'recomendacion': recomendacion,
            'es_usuario': user_type == 'usuario',
            'es_empresa': user_type == 'empresa',
            'num_likes': recomendacion.num_likes if recomendacion else 0,
            'usuarios_likes': usuarios_likes
        }
        
        return render(request, 'discover/detalle_recomendacion_subida.html', context)
        
    except Exception as e:
        messages.error(request, f"Error al cargar la recomendación: {str(e)}")
        return redirect('principal')
    