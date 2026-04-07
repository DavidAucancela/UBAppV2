"""
Middleware para capturar el usuario actual en thread-local.
Permite que signals y modelos accedan al usuario de la request.
"""
import threading


class JWTCookieMiddleware:
    """
    Lee el access_token de la cookie httpOnly y lo inyecta en HTTP_AUTHORIZATION,
    permitiendo que simplejwt autentique sin necesidad de que el frontend gestione el header.
    Solo actúa si no hay ya un header Authorization presente.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'HTTP_AUTHORIZATION' not in request.META:
            token = request.COOKIES.get('access_token')
            if token:
                request.META['HTTP_AUTHORIZATION'] = f'Bearer {token}'
        return self.get_response(request)

_thread_locals = threading.local()


def get_current_user():
    return getattr(_thread_locals, 'user', None)


def get_current_ip():
    return getattr(_thread_locals, 'ip_address', None)


class CurrentUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            user = getattr(request, 'user', None)
            _thread_locals.user = user if user and user.is_authenticated else None
        except Exception:
            _thread_locals.user = None
        _thread_locals.ip_address = self._get_client_ip(request)

        response = self.get_response(request)

        _thread_locals.user = None
        _thread_locals.ip_address = None
        return response

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
