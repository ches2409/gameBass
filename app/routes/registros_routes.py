from flask import Blueprint, render_template, request

from app.services import (
    torneos_services,
    juegos_services,
    usuarios_services,
    roles_services,
    equipos_services,
    dashboard_service,
)

registros_bp = Blueprint("registro", __name__, url_prefix="/registros")


@registros_bp.route("/")
def index():
    torneos_list = torneos_services.get_all_torneos()
    juegos_list = juegos_services.get_all_games()
    usuarios_list = usuarios_services.get_all_usuarios()
    roles_list = roles_services.get_all_roles()
    equipos_list = equipos_services.get_all_equipos()
    context = dashboard_service.get_dashboard_data(request.path)

    return render_template(
        "dashboard/registros.html",
        torneos=torneos_list,
        juegos=juegos_list,
        usuarios=usuarios_list,
        roles=roles_list,
        equipos=equipos_list,
        **context
    )


@registros_bp.route("/create", methods=["POST"])
def create():
    pass
