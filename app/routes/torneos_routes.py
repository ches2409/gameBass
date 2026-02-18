from flask import Blueprint, request, render_template, redirect, url_for

from app.enums.tipos import EstadoTorneo
from app.services import dashboard_service, torneos_services, juegos_services

torneos_bp = Blueprint("torneo", __name__, url_prefix="/torneos")


@torneos_bp.route("/")
def index():

    context = dashboard_service.get_dashboard_data(request.path)

    torneos_list = torneos_services.get_all_torneos()
    juegos_list = juegos_services.get_all_games()

    return render_template(
        "dashboard/torneos.html",
        torneos_list=torneos_list,
        juegos_list=juegos_list,
        estados=EstadoTorneo,
        **context,
    )


@torneos_bp.route("/create", methods=["POST"])
def create():

    nombre_torneo = request.form.get("nombre_de_torneo")
    recompensa_torneo = request.form.get("recompensa_de_torneo")
    nivel_acceso_min = request.form.get("nivel_de_acceso_minimo")
    estado_torneo = request.form.get("estado_de_torneo")
    max_competidores = request.form.get("max_de_competidores")
    fecha_inicio = request.form.get("fecha_de_inicio")
    fecha_fin = request.form.get("fecha_de_fin")
    id_juego = request.form.get("id_de_juego")

    torneos_services.create_torneo(
        nombre_torneo,
        recompensa_torneo,
        nivel_acceso_min,
        estado_torneo,
        max_competidores,
        fecha_inicio,
        fecha_fin,
        id_juego,
    )

    return redirect(url_for("torneo.index"))


@torneos_bp.route("/update/<int:id_torneo>", methods=["POST"])
def update(id_torneo):

    torneo = torneos_services.get_torneos_by_id(id_torneo)

    if not torneo:
        raise ValueError(f"El torneo con ID {id_torneo} no existe.")

    nombre_torneo = request.form.get("nombre_de_torneo")
    recompensa_torneo = request.form.get("recompensa_de_torneo")
    nivel_acceso_min = request.form.get("nivel_de_acceso_minimo")
    estado_torneo = request.form.get("estado_de_torneo")
    max_competidores = request.form.get("max_de_competidores")
    fecha_inicio = request.form.get("fecha_de_inicio")
    fecha_fin = request.form.get("fecha_de_fin")
    id_juego = request.form.get("id_de_juego")

    torneos_services.update_torneo(
        id_torneo,
        nombre_torneo,
        recompensa_torneo,
        nivel_acceso_min,
        estado_torneo,
        max_competidores,
        fecha_inicio,
        fecha_fin,
        id_juego,
    )

    return redirect(url_for("torneo.index"))


@torneos_bp.route("/delete/<int:id_torneo>")
def delete(id_torneo):

    torneos_services.delete_torneo(id_torneo)

    return redirect(url_for("torneo.index"))
