from django.utils import translation


class UserLanguageMiddleware:
    """Активирует язык пользователя из базы данных на каждый запрос."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            lang = getattr(request.user, 'interface_language', None) or 'ru'
            translation.activate(lang)
            request.LANGUAGE_CODE = lang
        response = self.get_response(request)
        return response