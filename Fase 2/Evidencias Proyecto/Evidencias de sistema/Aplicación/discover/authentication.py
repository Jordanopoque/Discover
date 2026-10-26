from dataclasses import dataclass

from rest_framework.authentication import CSRFCheck
from rest_framework.exceptions import PermissionDenied

from discover.models import Administrador, Empresa, Usuario


@dataclass(frozen=True)
class DiscoverPrincipal:
    id: int
    user_type: str
    account: object

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False


def get_discover_session_principal(session):
    user_type = session.get('user_type')
    user_id = session.get('user_id')
    account_models = {
        'usuario': Usuario,
        'empresa': Empresa,
        'administrador': Administrador,
    }
    model = account_models.get(user_type)

    if model is None:
        return None

    try:
        account_id = int(user_id)
        account = model.objects.get(pk=account_id)
    except (TypeError, ValueError, model.DoesNotExist):
        return None

    if getattr(account, 'is_active', True) is False:
        return None
    if getattr(account, 'is_blocked', False):
        return None

    return DiscoverPrincipal(
        id=account_id,
        user_type=user_type,
        account=account,
    )


def enforce_discover_csrf(request):
    http_request = getattr(request, '_request', request)
    check = CSRFCheck(lambda _: None)
    check.process_request(http_request)
    reason = check.process_view(http_request, None, (), {})
    if reason:
        raise PermissionDenied(f'CSRF Failed: {reason}')
