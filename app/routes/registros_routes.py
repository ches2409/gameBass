from flask import Blueprint, request, render_template, redirect, url_for, flash
from app.services import (
    dashboard_service,
    registros_services,
    torneos_services,
    equipos_services,
)
from flask_login import current_user

registros_bp = Blueprint("registro", __name__, url_prefix="/registros")


@registros_bp.route("/")
def index():
    context = dashboard_service.get_dashboard_data(request.path)

    # 1. Obtener datos para el formulario
    torneos = torneos_services.get_all_torneos()
    equipos = (
        equipos_services.get_all_equipos()
    )  # O filtrar solo los del usuario si prefieres

    # 2. Obtener los LOGS (Registros recientes)
    recent_logs = registros_services.get_recent_registros(limit=8)

    return render_template(
        "dashboard/registros.html",
        torneos=torneos,
        equipos=equipos,
        logs=recent_logs,  # Pasamos los logs a la plantilla
        **context,
    )


@registros_bp.route("/create", methods=["POST"])
def create():
    # Obtener datos del formulario
    modo = request.form.get("modo_registro")
    id_torneo = request.form.get("id_torneo")
    id_equipo = request.form.get("id_equipo") if modo == "equipo" else None

    # Datos automáticos del usuario actual
    id_usuario = current_user.id_usuario
    id_rol = 1  # Aquí deberías definir lógica para seleccionar el rol si aplica, o usar uno por defecto

    # Buscamos el torneo para saber el juego (necesario para el modelo Registro)
    torneo = torneos_services.get_torneo_by_id(id_torneo)
    id_juego = torneo.id_juego if torneo else None

    try:
        if id_torneo and id_juego:
            registros_services.create_registro(
                puntaje=0,
                id_torneo=id_torneo,
                id_juego=id_juego,
                id_usuario=id_usuario,
                id_rol=id_rol,
                id_equipo=id_equipo,
            )
            flash("Sincronización con Arena completada exitosamente.", "success")
        else:
            flash(
                "Error de enlace: No se pudo identificar el Torneo o el Juego base.",
                "warning",
            )

    except ValueError as e:
        flash(f"Error de validación: {str(e)}", "danger")
    except Exception as e:
        flash(f"Fallo crítico del sistema: {str(e)}", "danger")

    return redirect(url_for("registro.index"))
