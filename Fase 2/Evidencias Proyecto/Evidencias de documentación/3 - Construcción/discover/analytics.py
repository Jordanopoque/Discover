from datetime import date, datetime, time, timedelta
from collections import Counter

from django.conf import settings
from django.db.models import Avg, Count, Q, Sum
from django.utils import timezone

from .models import (
    Empresa,
    Genero,
    MeGusta,
    Recomendacion,
    RecomendacionGuardada,
    Reporte,
    SesionActividad,
    TipoRecomendacion,
    Usuario,
)
from .session_activity import finalize_idle_sessions


def _selected_dates(params):
    today = timezone.localdate()
    raw_start = params.get('desde', '').strip()
    raw_end = params.get('hasta', '').strip()
    try:
        end = date.fromisoformat(raw_end) if raw_end else today
        start = date.fromisoformat(raw_start) if raw_start else end - timedelta(days=29)
    except ValueError:
        return today - timedelta(days=29), today, 'El rango de fechas no es válido.'
    if start > end:
        return today - timedelta(days=29), today, 'La fecha inicial debe ser anterior a la fecha final.'
    return start, end, ''


def _recommendation_filter(params):
    filters = {}
    filter_error = ''
    selected_type = params.get('tipo', '').strip()
    selected_genre = params.get('genero', '').strip()
    if selected_type:
        if not selected_type.isdigit() or not TipoRecomendacion.objects.filter(pk=selected_type).exists():
            filter_error = 'El tipo de contenido seleccionado no es válido.'
            filters['tipo_id'] = -1
            selected_type = ''
        else:
            filters['tipo_id'] = int(selected_type)
    if selected_genre:
        if not selected_genre.isdigit():
            filter_error = 'El género seleccionado no es válido.'
            filters['genero_id'] = -1
            selected_genre = ''
        else:
            genre = Genero.objects.filter(pk=selected_genre).first()
            if genre is None or (selected_type and genre.tipo_recomendacion_id != int(selected_type)):
                filter_error = 'El género seleccionado no corresponde al tipo de contenido.'
                filters['genero_id'] = -1
                selected_genre = ''
            else:
                filters['genero_id'] = int(selected_genre)
                if not selected_type:
                    selected_type = str(genre.tipo_recomendacion_id)
                    filters['tipo_id'] = genre.tipo_recomendacion_id
    return filters, selected_type, selected_genre, filter_error


def _date_range_kwargs(field, start, end):
    start_datetime = timezone.make_aware(datetime.combine(start, time.min))
    end_datetime = timezone.make_aware(
        datetime.combine(end + timedelta(days=1), time.min)
    )
    return {
        f'{field}__gte': start_datetime,
        f'{field}__lt': end_datetime,
    }


def _date_range_q(field, start, end):
    return Q(**_date_range_kwargs(field, start, end))


def _range_filter(queryset, field, start, end):
    return queryset.filter(**_date_range_kwargs(field, start, end))


def _period_ranges(start, end):
    monthly = (end - start).days > 62
    periods = []
    if not monthly:
        current = start
        while current <= end:
            periods.append((
                current.strftime('%d/%m'),
                current,
                current,
            ))
            current += timedelta(days=1)
        return periods

    current = date(start.year, start.month, 1)
    while current <= end:
        next_month = date(current.year + (current.month == 12), current.month % 12 + 1, 1)
        period_start = max(start, current)
        period_end = min(end, next_month - timedelta(days=1))
        periods.append((
            current.strftime('%b %Y'),
            period_start,
            period_end,
        ))
        current = next_month
    return periods


def _interaction_counts(recommendation_ids, start, end):
    saved = _range_filter(
        RecomendacionGuardada.objects.filter(recomendacion_id__in=recommendation_ids),
        'fecha_guardado',
        start,
        end,
    ).count()
    likes = _range_filter(
        MeGusta.objects.filter(recomendacion_id__in=recommendation_ids),
        'fecha',
        start,
        end,
    ).count()
    return saved, likes


def _build_trend(recommendation_ids, start, end):
    periods = _period_ranges(start, end)
    saved_queryset = RecomendacionGuardada.objects.filter(
        recomendacion_id__in=recommendation_ids,
    )
    likes_queryset = MeGusta.objects.filter(recomendacion_id__in=recommendation_ids)
    saved_counts = saved_queryset.aggregate(**{
        f'period_{index}': Count(
            'id',
            filter=_date_range_q('fecha_guardado', period_start, period_end),
        )
        for index, (_, period_start, period_end) in enumerate(periods)
    })
    like_counts = likes_queryset.aggregate(**{
        f'period_{index}': Count(
            'id',
            filter=_date_range_q('fecha', period_start, period_end),
        )
        for index, (_, period_start, period_end) in enumerate(periods)
    })
    return [
        {
            'label': label,
            'value': (saved_counts[f'period_{index}'] or 0)
            + (like_counts[f'period_{index}'] or 0),
        }
        for index, (label, _, _) in enumerate(periods)
    ]


def _build_session_trend(sessions, start, end):
    periods = _period_ranges(start, end)
    averages = sessions.aggregate(**{
        f'period_{index}': Avg(
            'duration_seconds',
            filter=_date_range_q('started_at', period_start, period_end),
        )
        for index, (_, period_start, period_end) in enumerate(periods)
    })
    return [
        {
            'label': label,
            'value': round(averages[f'period_{index}'] / 60, 1)
            if averages[f'period_{index}'] is not None else None,
        }
        for index, (label, _, _) in enumerate(periods)
    ]


def get_admin_session_activity_snapshot(params):
    start, end, _ = _selected_dates(params)
    start_datetime = timezone.make_aware(datetime.combine(start, time.min))
    end_datetime = timezone.make_aware(
        datetime.combine(end + timedelta(days=1), time.min)
    )
    sessions = SesionActividad.objects.filter(
        user_type='usuario',
        started_at__gte=start_datetime,
        started_at__lt=end_datetime,
    )
    finalize_idle_sessions(sessions)
    return [
        {
            'id': activity.id,
            'status': activity.activity_status,
            'duration_seconds': activity.duration_seconds,
            'last_activity_at': timezone.localtime(activity.last_activity_at).isoformat(),
            'last_activity_date': timezone.localtime(
                activity.last_activity_at
            ).date().isoformat(),
            'last_activity_display': timezone.localtime(
                activity.last_activity_at
            ).strftime('%d/%m/%Y %H:%M'),
        }
        for activity in sessions
    ]


def build_admin_dashboard_context(params):
    start, end, date_error = _selected_dates(params)
    recommendation_filters, selected_type, selected_genre, selection_error = (
        _recommendation_filter(params)
    )
    metric = params.get('metrica', 'interacciones')
    if metric not in {'interacciones', 'guardados', 'me_gusta'}:
        metric = 'interacciones'

    published = _range_filter(
        Recomendacion.objects.filter(
            estado_aprobacion__nombre='aprobado',
            **recommendation_filters,
        ),
        'fecha_creacion',
        start,
        end,
    )
    eligible = Recomendacion.objects.filter(
        estado_aprobacion__nombre='aprobado',
        **recommendation_filters,
    )
    recommendation_ids = eligible.values_list('id', flat=True)
    saved_total, likes_total = _interaction_counts(recommendation_ids, start, end)

    previous_days = (end - start).days + 1
    previous_end = start - timedelta(days=1)
    previous_start = previous_end - timedelta(days=previous_days - 1)
    previous_saved, previous_likes = _interaction_counts(
        recommendation_ids, previous_start, previous_end
    )
    current_interactions = saved_total + likes_total
    previous_interactions = previous_saved + previous_likes
    interaction_change = None
    if previous_interactions:
        interaction_change = round(
            (current_interactions - previous_interactions) * 100 / previous_interactions,
            1,
        )

    start_datetime = timezone.make_aware(datetime.combine(start, time.min))
    end_datetime = timezone.make_aware(datetime.combine(end + timedelta(days=1), time.min))
    previous_start_datetime = timezone.make_aware(
        datetime.combine(previous_start, time.min)
    )
    previous_end_datetime = timezone.make_aware(
        datetime.combine(previous_end + timedelta(days=1), time.min)
    )
    sessions = SesionActividad.objects.filter(
        user_type='usuario',
        started_at__gte=start_datetime,
        started_at__lt=end_datetime,
    )
    finalize_idle_sessions(sessions)
    previous_sessions = SesionActividad.objects.filter(
        user_type='usuario',
        started_at__gte=previous_start_datetime,
        started_at__lt=previous_end_datetime,
    )
    session_rows = list(sessions)
    session_emails = dict(
        Usuario.objects.filter(
            pk__in={activity.account_id for activity in session_rows}
        ).values_list('pk', 'correo')
    )
    for activity in session_rows:
        activity.account_email = session_emails.get(
            activity.account_id, 'No disponible'
        )
    session_count = sessions.count()
    session_seconds = sessions.aggregate(total=Sum('duration_seconds'))['total'] or 0
    average_seconds = round(session_seconds / session_count) if session_count else 0
    previous_session_count = previous_sessions.count()
    previous_session_seconds = (
        previous_sessions.aggregate(total=Sum('duration_seconds'))['total'] or 0
    )
    previous_average_seconds = (
        previous_session_seconds / previous_session_count
        if previous_session_count else 0
    )
    session_duration_change = None
    if previous_average_seconds:
        session_duration_change = round(
            (average_seconds - previous_average_seconds)
            * 100 / previous_average_seconds,
            1,
        )
    active_users = sessions.values('account_id').distinct().count()
    session_hours = Counter(
        timezone.localtime(started_at).hour
        for started_at in sessions.values_list('started_at', flat=True)
    )

    popularity = eligible.annotate(
        saved_count=Count(
            'recomendacionguardada',
            filter=_date_range_q(
                'recomendacionguardada__fecha_guardado', start, end
            ),
            distinct=True,
        ),
        like_count=Count(
            'megusta',
            filter=_date_range_q('megusta__fecha', start, end),
            distinct=True,
        ),
    )
    ranking = []
    for recommendation in popularity.select_related('tipo', 'genero'):
        total = recommendation.saved_count + recommendation.like_count
        score = {
            'guardados': recommendation.saved_count,
            'me_gusta': recommendation.like_count,
            'interacciones': total,
        }[metric]
        if score:
            ranking.append({
                'titulo': recommendation.titulo,
                'tipo': recommendation.tipo.nombre,
                'genero': recommendation.genero.nombre,
                'guardados': recommendation.saved_count,
                'me_gusta': recommendation.like_count,
                'interacciones': total,
                'score': score,
            })
    ranking.sort(key=lambda item: (-item['score'], item['titulo'].lower()))
    ranking = ranking[:10]

    types = TipoRecomendacion.objects.all().order_by('nombre')
    type_stats = list(
        eligible.values('tipo_id', 'tipo__nombre')
        .annotate(
            publicadas=Count(
                'id',
                filter=_date_range_q('fecha_creacion', start, end),
                distinct=True,
            ),
            guardados=Count(
                'recomendacionguardada',
                filter=_date_range_q(
                    'recomendacionguardada__fecha_guardado', start, end
                ),
                distinct=True,
            ),
            me_gusta=Count(
                'megusta',
                filter=_date_range_q('megusta__fecha', start, end),
                distinct=True,
            ),
        )
        .order_by('tipo__nombre')
    )
    type_stats_by_id = {item['tipo_id']: item for item in type_stats}
    type_stats = []
    for content_type in types:
        if selected_type and content_type.pk != int(selected_type):
            continue
        stats = type_stats_by_id.get(content_type.pk, {
            'publicadas': 0,
            'guardados': 0,
            'me_gusta': 0,
        })
        stats['nombre'] = content_type.nombre
        stats['interacciones'] = stats['guardados'] + stats['me_gusta']
        type_stats.append(stats)
    type_interactions = sum(item['interacciones'] for item in type_stats)
    for item in type_stats:
        item['porcentaje'] = round(
            item['interacciones'] * 100 / type_interactions, 1
        ) if type_interactions else 0

    genre_stats = list(
        eligible.values(
            'genero_id',
            'genero__nombre',
            'genero__tipo_recomendacion__nombre',
        )
        .annotate(
            publicadas=Count(
                'id',
                filter=_date_range_q('fecha_creacion', start, end),
                distinct=True,
            ),
            guardados=Count(
                'recomendacionguardada',
                filter=_date_range_q(
                    'recomendacionguardada__fecha_guardado', start, end
                ),
                distinct=True,
            ),
            me_gusta=Count(
                'megusta',
                filter=_date_range_q('megusta__fecha', start, end),
                distinct=True,
            ),
        )
    )
    genre_stats_by_id = {item['genero_id']: item for item in genre_stats}
    genre_queryset = Genero.objects.select_related('tipo_recomendacion')
    if selected_type:
        genre_queryset = genre_queryset.filter(tipo_recomendacion_id=selected_type)
    if selected_genre:
        genre_queryset = genre_queryset.filter(pk=selected_genre)
    genre_stats = []
    for genre in genre_queryset.order_by('nombre'):
        stats = genre_stats_by_id.get(genre.pk, {
            'publicadas': 0,
            'guardados': 0,
            'me_gusta': 0,
        })
        stats['nombre'] = genre.nombre
        stats['tipo'] = genre.tipo_recomendacion.nombre
        stats['interacciones'] = stats['guardados'] + stats['me_gusta']
        genre_stats.append(stats)
    genre_stats.sort(key=lambda item: (-item['interacciones'], item['nombre'].lower()))
    interactions_by_type = {}
    for item in genre_stats:
        interactions_by_type[item['tipo']] = (
            interactions_by_type.get(item['tipo'], 0) + item['interacciones']
        )
    for item in genre_stats:
        type_interactions = interactions_by_type[item['tipo']]
        item['porcentaje'] = round(
            item['interacciones'] * 100 / type_interactions, 1
        ) if type_interactions else 0
    genre_stats = genre_stats[:12]

    trend = _build_trend(recommendation_ids, start, end)
    session_trend = _build_session_trend(sessions, start, end)
    peak_hour = max(session_hours, key=session_hours.get) if session_hours else None
    top_type = max(type_stats, key=lambda item: item['interacciones'], default=None)
    top_genre = max(genre_stats, key=lambda item: item['interacciones'], default=None)

    return {
        'pendientes': Recomendacion.objects.filter(
            estado_aprobacion__nombre='pendiente'
        ).count(),
        'usuarios': Usuario.objects.count(),
        'empresas': Empresa.objects.count(),
        'reportes_pendientes': Reporte.objects.filter(estado='pendiente').count(),
        'recomendaciones_totales': Recomendacion.objects.filter(
            **recommendation_filters
        ).count(),
        'total_recomendaciones': published.count(),
        'total_guardados': saved_total,
        'total_me_gusta': likes_total,
        'total_interacciones': current_interactions,
        'usuarios_activos': active_users,
        'sesiones_total': session_count,
        'tiempo_total_minutos': round(session_seconds / 60, 1),
        'tiempo_promedio_minutos': round(average_seconds / 60, 1),
        'hora_pico': peak_hour,
        'sesiones_recientes': session_rows,
        'ranking': ranking,
        'tipos_stats': type_stats,
        'generos_stats': genre_stats,
        'tendencia': trend,
        'tendencia_sesiones': session_trend,
        'variacion_permanencia': session_duration_change,
        'metrica_actual': metric,
        'tipo_actual': selected_type,
        'genero_actual': selected_genre,
        'tipos_filtro': types,
        'generos_filtro': Genero.objects.select_related('tipo_recomendacion').order_by(
            'tipo_recomendacion__nombre', 'nombre'
        ),
        'desde': start.isoformat(),
        'hasta': end.isoformat(),
        'error_filtro': date_error or selection_error,
        'variacion_interacciones': interaction_change,
        'tipo_mas_interacciones': top_type,
        'genero_mas_interacciones': top_genre,
        'umbral_inactividad_minutos': getattr(
            settings, 'DISCOVER_ANALYTICS_SESSION_IDLE_MINUTES', 30
        ),
    }
