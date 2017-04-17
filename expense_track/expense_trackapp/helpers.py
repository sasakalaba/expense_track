from django.core.exceptions import ValidationError


def confirm_password(password1, password2):
    if password1 != password2:
        raise ValidationError('Passwords must match.')
