import hashlib
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from .models import SesionActividad


def _session_hash(session_key):
    return hashlib.sha256(session_key.encode('utf-8')).hexdigest()


def start_session_activity(request):
    session_key = request.session.session_key
    if not session_key:
        request.session.save()
        session_key = request.session.session_key
    if not session_key:
        return
    user_type = request.session.get('user_type')
    account_id = request.session.get('user_id')
    if user_type not in {'usuario', 'empresa', 'administrador'} or not account_id:
        return
    now = timezone.now()
    session_hash = _session_hash(session_key)
    SesionActividad.objects.filter(
        session_key_hash=session_hash,
        ended_at__isnull=True,
    ).update(ended_at=now)
    SesionActividad.objects.create(
        session_key_hash=session_hash,
        user_type=user_type,
        account_id=account_id,
        started_at=now,
        last_activity_at=now,
    )


def update_session_activity(request):
    session_key = request.session.session_key
    user_type = request.session.get('user_type')
    account_id = request.session.get('user_id')
    if not session_key or not account_id or user_type not in {
        'usuario', 'empresa', 'administrador'
    }:
        return

    now = timezone.now()
    activity = SesionActividad.objects.filter(
        session_key_hash=_session_hash(session_key),
        ended_at__isnull=True,
    ).order_by('-started_at').first()
    if activity is None:
        start_session_activity(request)
        return

    idle_minutes = getattr(settings, 'DISCOVER_ANALYTICS_SESSION_IDLE_MINUTES', 30)
    if now - activity.last_activity_at > timedelta(minutes=idle_minutes):
        activity.ended_at = now
        activity.save(update_fields=['ended_at'])
        start_session_activity(request)
        return

    activity.last_activity_at = now
    activity.duration_seconds = max(
        0, int((now - activity.started_at).total_seconds())
    )
    activity.save(update_fields=['last_activity_at', 'duration_seconds'])


def finalize_idle_sessions(queryset=None):
    now = timezone.now()
    idle_minutes = getattr(settings, 'DISCOVER_ANALYTICS_SESSION_IDLE_MINUTES', 30)
    stale_sessions = queryset if queryset is not None else SesionActividad.objects.all()
    return stale_sessions.filter(
        ended_at__isnull=True,
        last_activity_at__lt=now - timedelta(minutes=idle_minutes),
    ).update(ended_at=now)


def end_session_activity(request):
    session_key = request.session.session_key
    if not session_key:
        return
    activity = SesionActividad.objects.filter(
        session_key_hash=_session_hash(session_key),
        ended_at__isnull=True,
    ).order_by('-started_at').first()
    if activity is None:
        return
    now = timezone.now()
    activity.last_activity_at = now
    activity.ended_at = now
    activity.duration_seconds = max(
        0, int((now - activity.started_at).total_seconds())
    )
    activity.save(update_fields=[
        'last_activity_at', 'ended_at', 'duration_seconds'
    ])
