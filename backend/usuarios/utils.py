"""
Utilidades para el módulo de usuarios
"""
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import re
from typing import Optional

def enviar_email_verificacion(usuario, request=None):
    """
    Envía un email de verificación al usuario
    """
    token = usuario.generar_token_verificacion()
    
    # Construir URL de verificación
    if request:
        protocol = 'https' if request.is_secure() else 'http'
        domain = request.get_host()
    else:
        protocol = 'http'
        domain = 'localhost:4200'  # Frontend Angular
    
    verification_url = f"{protocol}://{domain}/verify-email?token={token}&user={usuario.id}"
    
    subject = 'Verificación de cuenta - Sistema de Almacenamiento'
    
    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #333;">¡Bienvenido {usuario.nombre or usuario.username}!</h2>
            <p>Gracias por registrarte en nuestro Sistema de Almacenamiento de Envíos.</p>
            <p>Para completar tu registro, por favor verifica tu dirección de correo electrónico haciendo clic en el siguiente enlace:</p>
            <p style="margin: 30px 0;">
                <a href="{verification_url}" 
                   style="background-color: #4CAF50; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                    Verificar mi cuenta
                </a>
            </p>
            <p>O copia y pega este enlace en tu navegador:</p>
            <p style="background-color: #f4f4f4; padding: 10px; border-radius: 5px; word-break: break-all;">
                {verification_url}
            </p>
            <p><strong>Este enlace expirará en 24 horas.</strong></p>
            <hr style="border: 1px solid #eee; margin: 30px 0;">
            <p style="color: #666; font-size: 12px;">
                Si no creaste esta cuenta, puedes ignorar este correo de forma segura.
            </p>
        </body>
    </html>
    """
    
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [usuario.correo],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error enviando email de verificación: {e}")
        return False

def enviar_email_recuperacion(usuario, request=None):
    """
    Envía un email de recuperación de contraseña
    """
    token = usuario.generar_token_recuperacion()
    
    # Construir URL de recuperación
    if request:
        protocol = 'https' if request.is_secure() else 'http'
        domain = request.get_host()
    else:
        protocol = 'http'
        domain = 'localhost:4200'  # Frontend Angular
    
    reset_url = f"{protocol}://{domain}/reset-password?token={token}&user={usuario.id}"
    
    subject = 'Recuperación de contraseña - Sistema de Almacenamiento'
    
    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #333;">Recuperación de contraseña</h2>
            <p>Hola {usuario.nombre or usuario.username},</p>
            <p>Hemos recibido una solicitud para restablecer tu contraseña.</p>
            <p>Para crear una nueva contraseña, haz clic en el siguiente enlace:</p>
            <p style="margin: 30px 0;">
                <a href="{reset_url}" 
                   style="background-color: #FF9800; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                    Restablecer contraseña
                </a>
            </p>
            <p>O copia y pega este enlace en tu navegador:</p>
            <p style="background-color: #f4f4f4; padding: 10px; border-radius: 5px; word-break: break-all;">
                {reset_url}
            </p>
            <p><strong>Este enlace expirará en 2 horas por seguridad.</strong></p>
            <hr style="border: 1px solid #eee; margin: 30px 0;">
            <p style="color: #666; font-size: 12px;">
                Si no solicitaste este cambio, puedes ignorar este correo. Tu contraseña no será modificada.
            </p>
            <p style="color: #666; font-size: 12px;">
                Por seguridad, te recomendamos no compartir este enlace con nadie.
            </p>
        </body>
    </html>
    """
    
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [usuario.correo],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error enviando email de recuperación: {e}")
        return False

def enviar_notificacion_cambio_password(usuario):
    """
    Envía una notificación cuando se cambia la contraseña
    """
    subject = 'Tu contraseña ha sido cambiada - Sistema de Almacenamiento'
    
    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #333;">Contraseña actualizada</h2>
            <p>Hola {usuario.nombre or usuario.username},</p>
            <p>Te informamos que tu contraseña ha sido cambiada exitosamente.</p>
            <p><strong>Fecha y hora del cambio:</strong> {usuario.ultima_cambio_password.strftime('%d/%m/%Y %H:%M')}</p>
            <div style="background-color: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p style="margin: 0; color: #856404;">
                    <strong>⚠️ ¿No reconoces este cambio?</strong><br>
                    Si no fuiste tú quien cambió la contraseña, por favor contacta inmediatamente con el administrador del sistema.
                </p>
            </div>
            <hr style="border: 1px solid #eee; margin: 30px 0;">
            <p style="color: #666; font-size: 12px;">
                Este es un mensaje automático de seguridad. Por favor, no respondas a este correo.
            </p>
        </body>
    </html>
    """
    
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [usuario.correo],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error enviando notificación de cambio de contraseña: {e}")
        return False

def validar_password_seguro(password: str) -> tuple[bool, Optional[str]]:
    """
    Valida que la contraseña cumpla con las políticas de seguridad
    
    Políticas:
    - Mínimo 8 caracteres
    - Al menos una letra mayúscula
    - Al menos una letra minúscula
    - Al menos un número
    - Al menos un carácter especial
    - No puede contener espacios
    
    Returns:
        tuple: (es_valido, mensaje_error)
    """
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"
    
    if not re.search(r"[A-Z]", password):
        return False, "La contraseña debe contener al menos una letra mayúscula"
    
    if not re.search(r"[a-z]", password):
        return False, "La contraseña debe contener al menos una letra minúscula"
    
    if not re.search(r"\d", password):
        return False, "La contraseña debe contener al menos un número"
    
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password):
        return False, "La contraseña debe contener al menos un carácter especial"
    
    if " " in password:
        return False, "La contraseña no puede contener espacios"
    
    # Validaciones adicionales
    if len(password) > 128:
        return False, "La contraseña no puede tener más de 128 caracteres"
    
    # Verificar que no sea una contraseña común
    common_passwords = [
        'password', '12345678', 'qwerty', 'abc123', 'password123',
        'admin123', 'letmein', 'welcome', 'monkey', '1234567890'
    ]
    
    if password.lower() in common_passwords:
        return False, "Esta contraseña es muy común y no es segura"
    
    return True, None

def validar_datos_obligatorios(data: dict) -> tuple[bool, list]:
    """
    Valida que los datos obligatorios estén presentes
    
    Returns:
        tuple: (es_valido, lista_errores)
    """
    errores = []
    campos_obligatorios = {
        'username': 'Nombre de usuario',
        'nombre': 'Nombre completo',
        'correo': 'Correo electrónico',
        'cedula': 'Cédula',
        'rol': 'Rol'
    }
    
    for campo, nombre in campos_obligatorios.items():
        if campo not in data or not data[campo]:
            errores.append(f"El campo '{nombre}' es obligatorio")
    
    # Validar formato de correo
    if 'correo' in data and data['correo']:
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, data['correo']):
            errores.append("El formato del correo electrónico no es válido")
    
    # Validar cédula (formato ecuatoriano o general)
    if 'cedula' in data and data['cedula']:
        cedula = data['cedula']
        if not cedula.replace('-', '').replace(' ', '').isdigit():
            errores.append("La cédula debe contener solo números")
        elif len(cedula.replace('-', '').replace(' ', '')) < 8:
            errores.append("La cédula debe tener al menos 8 dígitos")
    
    # Validar teléfono si se proporciona
    if 'telefono' in data and data['telefono']:
        telefono = data['telefono']
        telefono_limpio = telefono.replace('-', '').replace(' ', '').replace('+', '')
        if not telefono_limpio.isdigit():
            errores.append("El teléfono debe contener solo números")
    
    return len(errores) == 0, errores
