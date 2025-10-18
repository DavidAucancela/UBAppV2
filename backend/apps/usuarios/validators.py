from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password as django_validate_password
import re


def validar_cedula_ecuatoriana(cedula: str) -> None:
    """Valida cédula ecuatoriana usando algoritmo módulo 10.

    Debe usarse como validador de Django (lanza ValidationError si no es válida).
    """
    if not cedula or len(cedula) != 10:
        raise ValidationError("La cédula debe tener 10 dígitos")

    if not cedula.isdigit():
        raise ValidationError("La cédula solo debe contener números")

    provincia = int(cedula[0:2])
    if provincia < 1 or provincia > 24:
        raise ValidationError("Los dos primeros dígitos deben estar entre 01 y 24 (código de provincia)")

    # Personas naturales
    if int(cedula[2]) >= 6:
        raise ValidationError("El tercer dígito debe ser menor a 6 para personas naturales")

    coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    suma = 0

    for i in range(9):
        valor = int(cedula[i]) * coeficientes[i]
        if valor >= 10:
            valor -= 9
        suma += valor

    resultado = suma % 10
    verificador = 0 if resultado == 0 else 10 - resultado

    if verificador != int(cedula[9]):
        raise ValidationError("El dígito verificador de la cédula no es válido")


def validar_password_fuerte(password: str) -> None:
    """Valida que la contraseña cumpla reglas de seguridad fuertes.

    Lanza ValidationError si la contraseña no cumple los requisitos.
    """
    if password is None:
        raise ValidationError("La contraseña es requerida")

    if len(password) < 8:
        raise ValidationError("La contraseña debe tener al menos 8 caracteres")

    if not any(c.isupper() for c in password):
        raise ValidationError("La contraseña debe contener al menos una letra mayúscula")

    if not any(c.islower() for c in password):
        raise ValidationError("La contraseña debe contener al menos una letra minúscula")

    if not any(c.isdigit() for c in password):
        raise ValidationError("La contraseña debe contener al menos un número")

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError("La contraseña debe contener al menos un carácter especial (!@#$%^&*...)")

    # Validaciones de Django (listas comunes, similitud, numérica)
    django_validate_password(password)


