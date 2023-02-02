from django.utils import timezone


def now(request):
    """Добавляет переменную с текущим годом."""
    return {'now': timezone.now()}
