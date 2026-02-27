from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user
from app.utils.permissions import Permissions

def permission_required(*allowed_levels):
    """
    Permite el acceso si el usuario tiene uno de los niveles exactos pasados como argumento.
    El ADMIN (100) siempre tiene acceso implícito.
    Uso: @permission_required(Permissions.MOD_TACTICO, Permissions.ADMIN)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 1. Verificación de Autenticación
            if not current_user.is_authenticated:
                flash("ACCESO DENEGADO: Debes iniciar sesión.", "warning")
                return redirect(url_for("auth.login"))

            user_level = current_user.jerarquia.nivel_acceso

            # 2. Verificación de Permisos (Lista Exacta + Admin Implícito)
            # Si el usuario NO es Admin Y su nivel NO está en la lista permitida...
            if user_level != Permissions.ADMIN and user_level not in allowed_levels:
                flash(
                    "ACCESO DENEGADO: Credenciales insuficientes para esta operación.",
                    "danger",
                )

                # Redirigimos al inicio general, para que este decorador sirva en cualquier ruta (Torneos, Usuarios, etc.)
                return redirect(url_for("index.index"))
            return f(*args, **kwargs)

        return decorated_function

    return decorator
