import base64
import hashlib
import json
import os
from datetime import datetime, timezone as datetime_timezone
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import patch
from urllib.error import HTTPError

from django.conf import settings
from django.test import RequestFactory, SimpleTestCase, TestCase
from django.core.cache import cache
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient, APIRequestFactory
from .models import (
    Administrador,
    Empresa,
    EstadoAprobacion,
    Genero,
    MeGusta,
    Recomendacion,
    RecomendacionGuardada,
    SesionActividad,
    TipoRecomendacion,
    Usuario,
)

from .views import generar_audio_recomendacion, generar_recomendacion_ia
from .api.views import login_usuario_api, logout_api


class TestSession(dict):
    expiry = None

    def flush(self):
        self.clear()

    def set_expiry(self, expiry):
        self.expiry = expiry


class GenerarRecomendacionIATests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def post(self, data):
        request = self.factory.post(
            '/generar-recomendacion-ia/',
            data=json.dumps(data),
            content_type='application/json',
        )
        request.session = {'user_id': 1}
        with patch(
            'discover.views.get_discover_session_principal',
            return_value=SimpleNamespace(user_type='usuario'),
        ):
            return generar_recomendacion_ia(request)

    @patch.dict(os.environ, {'GEMINI_API_KEY': ''})
    def test_requires_gemini_api_key(self):
        response = self.post({'titulo': 'Dune'})

        self.assertEqual(response.status_code, 503)
        self.assertIn('no está configurada', json.loads(response.content)['error'])

    def test_rejects_empty_title(self):
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}):
            response = self.post({'titulo': '  '})

        self.assertEqual(response.status_code, 400)

    @patch('discover.views.urlopen')
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    def test_returns_generated_recommendation_fields(self, mock_urlopen):
        mock_urlopen.return_value = BytesIO(json.dumps({
            'candidates': [{
                'content': {'parts': [{
                    'text': json.dumps({
                        'resumen': 'Una historia que vale la pena descubrir.',
                        'trivia': 'Su autor tardó años en terminarla.',
                        'frase_destacada': 'El viaje comienza aquí.',
                    })
                }]}
            }]
        }).encode('utf-8'))

        response = self.post({'titulo': 'Dune'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content),
            {
                'resumen': 'Una historia que vale la pena descubrir.',
                'trivia': 'Su autor tardó años en terminarla.',
                'frase_destacada': 'El viaje comienza aquí.',
            },
        )
        gemini_request = mock_urlopen.call_args.args[0]
        self.assertIn('Dune', gemini_request.data.decode('utf-8'))
        self.assertEqual(gemini_request.headers['Content-type'], 'application/json')
        self.assertIn('application/json', gemini_request.data.decode('utf-8'))

    @patch('discover.views.urlopen')
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    def test_rejects_incomplete_gemini_content(self, mock_urlopen):
        mock_urlopen.return_value = BytesIO(json.dumps({
            'candidates': [{
                'content': {'parts': [{'text': json.dumps({'resumen': 'Solo resumen'})}]}
            }]
        }).encode('utf-8'))

        response = self.post({'titulo': 'Dune'})

        self.assertEqual(response.status_code, 502)

    @patch('discover.views.urlopen')
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    def test_reports_model_configuration_on_gemini_404(self, mock_urlopen):
        mock_urlopen.side_effect = HTTPError(
            url='https://generativelanguage.googleapis.com/v1beta/models/invalid:generateContent',
            code=404,
            msg='Not Found',
            hdrs=None,
            fp=BytesIO(b'{"error":{"message":"model not found"}}'),
        )

        response = self.post({'titulo': 'Dune'})

        self.assertEqual(response.status_code, 502)
        self.assertIn(
            'no se pudo identificar un modelo disponible',
            json.loads(response.content)['error'].lower(),
        )

    @patch('discover.views.urlopen')
    @patch('discover.views.settings.GEMINI_MODEL', 'gemini-2.5-flash')
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    def test_retries_with_a_supported_model_after_404(self, mock_urlopen):
        mock_urlopen.side_effect = [
            HTTPError(
                url='https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent',
                code=404,
                msg='Not Found',
                hdrs=None,
                fp=BytesIO(b'{"error":{"message":"model not found"}}'),
            ),
            BytesIO(json.dumps({
                'models': [{
                    'name': 'models/gemini-3.5-flash-lite',
                    'supportedGenerationMethods': ['generateContent'],
                }]
            }).encode('utf-8')),
            BytesIO(json.dumps({
                'candidates': [{
                    'content': {'parts': [{
                        'text': json.dumps({
                            'resumen': 'Resumen',
                            'trivia': 'Trivia',
                            'frase_destacada': 'Frase',
                        })
                    }]}
                }]
            }).encode('utf-8')),
        ]

        response = self.post({'titulo': 'Dune'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mock_urlopen.call_args_list), 3)
        fallback_request = mock_urlopen.call_args_list[2].args[0]
        self.assertIn('gemini-3.5-flash-lite:generateContent', fallback_request.full_url)


class GenerarAudioRecomendacionTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        cache.clear()

    def post(self, data, authenticated=True):
        request = self.factory.post(
            '/generar-audio-recomendacion/',
            data=json.dumps(data),
            content_type='application/json',
        )
        request.session = {'user_id': 1} if authenticated else {}
        principal = SimpleNamespace(user_type='usuario') if authenticated else None
        with patch('discover.views.get_discover_session_principal', return_value=principal):
            return generar_audio_recomendacion(request)

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    @patch('discover.views.Recomendacion.objects.get')
    @patch('discover.views.urlopen')
    def test_generates_audio_from_only_the_requested_stored_section(
        self,
        mock_urlopen,
        mock_recomendacion_get,
    ):
        audio_bytes = b'RIFF\x04\x00\x00\x00WAVE'
        mock_recomendacion_get.return_value = SimpleNamespace(
            resumen='Texto exacto que debe leerse.',
            trivia='Trivia que no debe leerse.',
            frase_destacada='Frase que no debe leerse.',
        )
        mock_urlopen.return_value = BytesIO(json.dumps({
            'steps': [{
                'type': 'model_output',
                'content': [{
                    'type': 'audio',
                    'data': base64.b64encode(audio_bytes).decode('ascii'),
                }],
            }],
        }).encode('utf-8'))

        response = self.post({'recomendacion_id': 7, 'section': 'resumen'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'audio/wav')
        self.assertEqual(response.content, audio_bytes)
        gemini_request = mock_urlopen.call_args.args[0]
        self.assertEqual(
            gemini_request.full_url,
            'https://generativelanguage.googleapis.com/v1beta/interactions',
        )
        self.assertEqual(gemini_request.headers['X-goog-api-key'], 'test-key')
        payload = json.loads(gemini_request.data.decode('utf-8'))
        self.assertEqual(payload['model'], 'gemini-3.8-flash-lite-tts')
        self.assertEqual(
            payload['input'][0]['content'][0]['text'],
            'Texto exacto que debe leerse.',
        )
        self.assertEqual(payload['response_format'], {'type': 'audio'})

    @patch('discover.views.urlopen')
    @patch('discover.views.Recomendacion.objects.get')
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    def test_reuses_cached_audio_without_calling_gemini(
        self,
        mock_recomendacion_get,
        mock_urlopen,
    ):
        audio_bytes = b'RIFF\x04\x00\x00\x00WAVE'
        mock_recomendacion_get.return_value = SimpleNamespace(
            resumen='Texto exacto que debe leerse.',
            trivia='',
            frase_destacada='',
        )
        cache.set(
            'gemini-tts-v1:' + hashlib.sha256(
                'gemini-3.8-flash-lite-tts\0Kore\0resumen\0Texto exacto que debe leerse.'.encode('utf-8')
            ).hexdigest(),
            audio_bytes,
            timeout=60,
        )

        response = self.post({'recomendacion_id': 7, 'section': 'resumen'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, audio_bytes)
        mock_urlopen.assert_not_called()

    def test_requires_a_logged_in_user(self):
        response = self.post({'recomendacion_id': 7, 'section': 'resumen'}, authenticated=False)

        self.assertEqual(response.status_code, 401)

    def test_rejects_unknown_section(self):
        response = self.post({'recomendacion_id': 7, 'section': 'titulo'})

        self.assertEqual(response.status_code, 400)

    def test_rejects_non_string_section(self):
        response = self.post({'recomendacion_id': 7, 'section': []})

        self.assertEqual(response.status_code, 400)

    @patch('discover.views.Recomendacion.objects.get')
    def test_rejects_empty_section_text(self, mock_recomendacion_get):
        mock_recomendacion_get.return_value = SimpleNamespace(resumen='')

        response = self.post({'recomendacion_id': 7, 'section': 'resumen'})

        self.assertEqual(response.status_code, 400)


class SessionAuthenticationTests(SimpleTestCase):
    def setUp(self):
        self.client = APIClient(enforce_csrf_checks=True)

    def test_session_endpoint_reports_anonymous_without_server_session(self):
        response = self.client.get('/api/session/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['authenticated'], False)

    def test_protected_api_rejects_anonymous_request(self):
        response = self.client.get('/api/recomendaciones_guardadas_todas/')

        self.assertEqual(response.status_code, 403)

    def test_login_api_requires_csrf_token(self):
        response = self.client.post('/api/login/', {
            'correo': 'nobody@example.com',
            'contrasena': 'incorrecta',
            'tipo_usuario': 'usuario',
        })

        self.assertEqual(response.status_code, 403)

    def test_csrf_and_session_cookies_are_http_only_and_session_expires_with_browser(self):
        response = self.client.get('/api/csrf/')

        self.assertEqual(response.status_code, 200)
        self.assertIn('csrfToken', response.json())
        self.assertTrue(response.cookies['csrftoken']['httponly'])
        self.assertTrue(settings.SESSION_COOKIE_HTTPONLY)
        self.assertTrue(settings.SESSION_EXPIRE_AT_BROWSER_CLOSE)
        self.assertEqual(settings.SESSION_COOKIE_AGE, 60 * 60 * 8)

    @patch('discover.api.views.enforce_discover_csrf')
    @patch('discover.api.views.start_session_activity')
    @patch('discover.api.views.check_password', return_value=True)
    @patch('discover.api.views.Usuario.objects.get')
    def test_mobile_login_creates_a_browser_session(
        self,
        mock_get_user,
        mock_check_password,
        mock_start_activity,
        mock_enforce_csrf,
    ):
        mock_get_user.return_value = SimpleNamespace(
            id=17,
            contrasena='hashed',
            is_active=True,
            is_blocked=False,
        )
        session = TestSession({'old_session_value': 'discard'})
        request = APIRequestFactory().post('/api/login/', {
            'correo': 'reader@example.com',
            'contrasena': 'correct',
            'tipo_usuario': 'usuario',
        }, format='json')
        request.session = session

        response = login_usuario_api(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(session['user_id'], 17)
        self.assertEqual(session['user_type'], 'usuario')
        self.assertEqual(session.expiry, 0)
        self.assertNotIn('old_session_value', session)

    @patch('discover.api.authentication.enforce_discover_csrf')
    @patch('discover.api.authentication.get_discover_session_principal')
    @patch('discover.api.views.end_session_activity')
    @patch('discover.api.views.enforce_discover_csrf')
    def test_logout_flushes_the_server_session(
        self,
        mock_view_csrf,
        mock_end_activity,
        mock_get_principal,
        mock_auth_csrf,
    ):
        mock_get_principal.return_value = SimpleNamespace(user_type='usuario')
        session = TestSession({'user_id': 17, 'user_type': 'usuario'})
        request = APIRequestFactory().post('/api/logout/', {}, format='json')
        request.session = session

        response = logout_api(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(session, {})


class AdminDashboardTests(TestCase):
    def setUp(self):
        self.admin = Administrador.objects.create(
            correo='admin-dashboard@example.com',
            contrasena='not-used',
            p_nombre='Admin',
            p_apellido='Discover',
        )
        self.usuario = Usuario.objects.create(
            correo='reader-dashboard@example.com',
            contrasena='not-used',
            p_nombre='Reader',
            p_apellido='Test',
        )
        self.empresa = Empresa.objects.create(
            correo='company-dashboard@example.com',
            contrasena='not-used',
            nombre_empresa='Company Test',
        )
        self.aprobado, _ = EstadoAprobacion.objects.get_or_create(nombre='aprobado')
        self.pendiente, _ = EstadoAprobacion.objects.get_or_create(nombre='pendiente')
        self.tipo = TipoRecomendacion.objects.create(nombre='Libros dashboard')
        self.genero = Genero.objects.create(
            nombre='Fantasía dashboard',
            tipo_recomendacion=self.tipo,
        )
        self.recomendacion = Recomendacion.objects.create(
            titulo='Recomendación popular',
            tipo=self.tipo,
            genero=self.genero,
            estado_aprobacion=self.aprobado,
            usuario=self.usuario,
        )
        RecomendacionGuardada.objects.create(
            usuario=self.usuario,
            recomendacion=self.recomendacion,
        )
        MeGusta.objects.create(usuario=self.usuario, recomendacion=self.recomendacion)
        activity_start = timezone.now() - timezone.timedelta(minutes=10)
        SesionActividad.objects.create(
            session_key_hash='a' * 64,
            user_type='usuario',
            account_id=self.usuario.id,
            started_at=activity_start,
            last_activity_at=activity_start + timezone.timedelta(minutes=10),
            duration_seconds=600,
        )
        Recomendacion.objects.create(
            titulo='Recomendación pendiente',
            tipo=self.tipo,
            genero=self.genero,
            estado_aprobacion=self.pendiente,
            usuario=self.usuario,
        )
        session = self.client.session
        session['user_id'] = self.admin.id
        session['user_type'] = 'administrador'
        session.save()

    def test_dashboard_keeps_existing_counts_and_aggregates_real_interactions(self):
        response = self.client.get(reverse('panel_administrador'), {
            'tipo': str(self.tipo.id),
            'genero': str(self.genero.id),
            'metrica': 'guardados',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['pendientes'], 1)
        self.assertEqual(response.context['usuarios'], 1)
        self.assertEqual(response.context['empresas'], 1)
        self.assertEqual(response.context['total_recomendaciones'], 1)
        self.assertEqual(response.context['total_guardados'], 1)
        self.assertEqual(response.context['total_me_gusta'], 1)
        self.assertEqual(response.context['total_interacciones'], 2)
        self.assertEqual(response.context['usuarios_activos'], 1)
        self.assertEqual(response.context['sesiones_total'], 1)
        self.assertEqual(response.context['tiempo_promedio_minutos'], 10)
        self.assertContains(response, 'admin-session-status__dot')
        self.assertContains(response, 'is-online')
        self.assertContains(response, 'id="session-account-filter"')
        self.assertContains(response, 'id="session-start-filter"')
        self.assertContains(response, 'id="session-last-activity-filter"')
        self.assertContains(response, 'id="session-duration-sort"')
        self.assertContains(response, 'id="session-status-filter"')
        self.assertContains(
            response,
            f'data-session-account="Usuario #{self.usuario.id} {self.usuario.correo}"',
        )
        self.assertContains(response, '<th>Correo</th>')
        self.assertContains(response, f'<td data-session-email>{self.usuario.correo}</td>')
        self.assertContains(response, 'data-session-duration-seconds="600"')
        self.assertEqual(response.context['tipos_stats'][0]['interacciones'], 2)
        self.assertEqual(response.context['tipos_stats'][0]['porcentaje'], 100)
        self.assertEqual(response.context['generos_stats'][0]['porcentaje'], 100)
        self.assertIn(10, [point['value'] for point in response.context['tendencia_sesiones']])
        self.assertEqual(response.context['ranking'][0]['titulo'], 'Recomendación popular')
        self.assertContains(
            response,
            '<h1>Centro de Analítica <span>Discover</span></h1>',
        )
        self.assertContains(response, 'id="download-dashboard-report"')
        self.assertContains(response, 'id="admin-report-period"')
        self.assertContains(response, 'id="activity-trend"')
        self.assertContains(response, 'id="session-trend"')
        self.assertContains(response, 'class="admin-bar-row admin-genre-row"')
        self.assertContains(
            response,
            f'data-genre-name="{self.genero.nombre}"',
        )
        self.assertContains(response, 'id="genre-insight" role="tooltip"')
        self.assertContains(response, 'id="activity-trend-modal"')
        self.assertContains(response, 'id="activity-trend-expanded"')
        self.assertContains(response, 'id="activity-trend-modal-close"')
        self.assertContains(response, 'id="session-trend-modal"')
        self.assertContains(response, 'id="session-trend-expanded"')
        self.assertContains(response, 'id="session-trend-modal-close"')
        self.assertNotContains(response, 'Acciones Rápidas')
        self.assertTrue(
            SesionActividad.objects.filter(
                session_key_hash__isnull=False,
                user_type='administrador',
                account_id=self.admin.id,
            ).exists()
        )

    def test_date_filter_excludes_activity_outside_selected_period(self):
        response = self.client.get(reverse('panel_administrador'), {
            'desde': '2000-01-01',
            'hasta': '2000-01-31',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_recomendaciones'], 0)
        self.assertEqual(response.context['total_guardados'], 0)
        self.assertEqual(response.context['total_me_gusta'], 0)
        self.assertEqual(response.context['total_interacciones'], 0)

    def test_session_list_includes_all_rows_and_scroll_container_after_twenty(self):
        now = timezone.now()
        for index in range(20):
            started_at = now - timezone.timedelta(minutes=index + 1)
            SesionActividad.objects.create(
                session_key_hash=f'{index + 1:064x}',
                user_type='usuario',
                account_id=self.usuario.id,
                started_at=started_at,
                last_activity_at=started_at,
                duration_seconds=60,
            )

        response = self.client.get(reverse('panel_administrador'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['sesiones_recientes']), 21)
        self.assertEqual(response.content.decode().count('data-session-email'), 21)
        self.assertContains(response, 'id="admin-session-list-scroll"')

        snapshot = self.client.get(reverse('admin_session_activity_status'))
        self.assertEqual(len(snapshot.json()['sessions']), 21)

    def test_administrative_panel_keeps_existing_kpis_and_quick_actions(self):
        response = self.client.get(reverse('panel_administrativo'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['pendientes'], 1)
        self.assertEqual(response.context['usuarios'], 1)
        self.assertEqual(response.context['empresas'], 1)
        self.assertContains(response, 'Panel Administrativo')
        self.assertContains(response, 'Acciones Rápidas')
        self.assertContains(response, 'Gestionar Categorías')

    def test_non_admin_cannot_access_administrative_panel(self):
        session = self.client.session
        session['user_id'] = self.usuario.id
        session['user_type'] = 'usuario'
        session.save()

        response = self.client.get(reverse('panel_administrativo'))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))

    def test_idle_session_is_finalized_and_status_refreshes_while_dashboard_is_open(self):
        now = timezone.now()
        self.activity = SesionActividad.objects.get(user_type='usuario')
        self.activity.started_at = now - timezone.timedelta(minutes=50)
        self.activity.last_activity_at = now - timezone.timedelta(minutes=40)
        self.activity.duration_seconds = 600
        self.activity.save(update_fields=[
            'started_at', 'last_activity_at', 'duration_seconds'
        ])

        response = self.client.get(reverse('panel_administrador'))

        self.assertEqual(response.status_code, 200)
        self.activity.refresh_from_db()
        self.assertIsNotNone(self.activity.ended_at)
        self.assertEqual(self.activity.activity_status, 'Finalizada por inactividad')
        self.assertEqual(
            response.context['sesiones_recientes'][0].activity_status,
            'Finalizada por inactividad',
        )

    def test_session_dates_are_rendered_in_chile_local_time(self):
        started_at_utc = datetime(
            2026, 10, 15, 15, 0, tzinfo=datetime_timezone.utc
        )
        self.activity = SesionActividad.objects.get(user_type='usuario')
        self.activity.started_at = started_at_utc
        self.activity.last_activity_at = started_at_utc
        self.activity.save(update_fields=['started_at', 'last_activity_at'])

        dashboard = self.client.get(reverse('panel_administrador'))
        refreshed = self.client.get(reverse('admin_session_activity_status'))

        self.assertEqual(settings.TIME_ZONE, 'America/Santiago')
        self.assertContains(dashboard, '15/10/2026 12:00')
        self.assertEqual(
            refreshed.json()['sessions'][0]['last_activity_display'],
            '15/10/2026 12:00',
        )
        self.assertTrue(
            refreshed.json()['sessions'][0]['last_activity_at'].endswith('-03:00')
        )

    def test_session_status_endpoint_requires_admin(self):
        session = self.client.session
        session['user_id'] = self.usuario.id
        session['user_type'] = 'usuario'
        session.save()

        response = self.client.get(reverse('admin_session_activity_status'))

        self.assertEqual(response.status_code, 403)

    def test_non_admin_cannot_access_dashboard(self):
        session = self.client.session
        session['user_id'] = self.usuario.id
        session['user_type'] = 'usuario'
        session.save()

        response = self.client.get(reverse('panel_administrador'))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))
