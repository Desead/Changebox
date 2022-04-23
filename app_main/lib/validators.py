import decimal

from django.core.exceptions import ValidationError

from app_main.lib.remove_space_from_string import remove_space_from_string


def validate_string(value):
    value = str(value).replace(',', '.')
    value = remove_space_from_string(value)
    try:
        value = decimal.Decimal(value)
    except:
        raise ValidationError('%(value)s Значение должно быть числом', params={'value': value})

    if value < 0:
        raise ValidationError('%(value)s Значение не может быть меньше 0', params={'value': value})
