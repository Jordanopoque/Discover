from rest_framework.authentication import BaseAuthentication

from discover.authentication import enforce_discover_csrf, get_discover_session_principal


class DiscoverSessionAuthentication(BaseAuthentication):
    def authenticate(self, request):
        session = request.session
        if not session.get('user_id') or not session.get('user_type'):
            return None

        principal = get_discover_session_principal(session)
        if principal is None:
            session.flush()
            return None

        enforce_discover_csrf(request)
        return principal, None
