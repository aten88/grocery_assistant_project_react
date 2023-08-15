from django.core.exceptions import ValidationError


def unique_color_validator(value):
    '''Кастомный валидатор для проверки уникальности HEX-кода цвета.'''
    from .models import Tag

    if Tag.objects.filter(color=value).exists():
        raise ValidationError('HEX-код цвета должен быть уникальным.')
