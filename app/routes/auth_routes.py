from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app.services import usuarios_services

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # Si el usuario ya está logueado, lo mandamos al dashboard
    if current_user.is_authenticated:
        return redirect(url_for("index.index"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        remember = True if request.form.get("remember") else False

        # Busca al usuario por email
        user = usuarios_services.get_usuario_by_email(email)

        # Verifica si existe y si la contraseña es correcta
        if not user or not check_password_hash(user.password_usuario, password):
            flash("Credenciales inválidas. Verifique sus datos.", "danger")
            return redirect(url_for("auth.login"))

        # Si todo es correcto, inicia la sesión
        login_user(user, remember=remember)

        # --- PROTOCOLO DE REDIRECCIÓN INTELIGENTE ---

        # 1. Si el usuario venía de una página específica (parametro 'next'), lo devolvemos allí.
        next_page = request.args.get("next")
        if next_page:
            return redirect(next_page)

        # 2. Si no, decidimos su destino según su RANGO (Nivel de Acceso)
        nivel = user.jerarquia.nivel_acceso

        if nivel >= 80:  # Alto Mando / Admin -> Dashboard Principal
            return redirect(url_for("index.index"))
        elif nivel >= 50:  # Comandantes -> Gestión de Equipos
            return redirect(url_for("equipo.index"))
        else:  # Soldados / Usuarios Base -> Torneos (o su perfil si existiera ruta)
            return redirect(url_for("torneo.index"))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
