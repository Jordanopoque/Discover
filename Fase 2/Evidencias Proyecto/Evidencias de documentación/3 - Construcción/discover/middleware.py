from .session_activity import update_session_activity


class DiscoverSessionActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        update_session_activity(request)
        return self.get_response(request)
