from flask import (
    Blueprint,
    request,
    render_template,
    redirect,
    url_for,
    flash,
    current_app,
)
import math

from flask_login import login_required

from app.enums.tipos import EstadoEquipo
from app.services import dashboard_service, equipos_services, usuarios_services
from app.utils.decorators import permission_required
from app.utils.permissions import Profiles

equipos_bp = Blueprint("equipo", __name__, url_prefix="/equipos")


@equipos_bp.route("/")
def index():
    context = dashboard_service.get_dashboard_data(request.path)
    equipos_list = equipos_services.get_all_equipos()
    usuarios_list = usuarios_services.get_all_usuarios()

    return render_template(
        "dashboard/equipos.html",
        estados_equipo=EstadoEquipo,
        equipos=equipos_list,
        usuarios=usuarios_list,
        **context,
    )


@equipos_bp.route("/create", methods=["POST"])
@permission_required(*Profiles.TACTICO)
def create():

    try:
        nombre_equipo = request.form.get("nombre_equipo")
        lema_equipo = request.form.get("lema_equipo")
        maximo_miembros = request.form.get("maximo_miembros")
        color_equipo = request.form.get("color_equipo")
        estado_equipo = request.form.get("estado_equipo")
        id_comandante = request.form.get("id_comandante")

        equipos_services.create_equipo(
            nombre_equipo,
            lema_equipo,
            maximo_miembros,
            color_equipo,
            estado_equipo,
            id_comandante,
        )

        # 1. MENSAJE DE ÉXITO
        flash(f"UNIDAD TÁCTICA '{nombre_equipo}' INYECTADA CORRECTAMENTE", "success")
    except Exception as e:
        # 2. MENSAJE DE ERROR
        flash(f"ERROR EN LA INYECCIÓN: {str(e)}", "danger")

    return redirect(url_for("equipo.index"))


@equipos_bp.route("/update/<int:id_equipo>", methods=["POST"])
@permission_required(*Profiles.TACTICO)
def update(id_equipo):

    equipo = equipos_services.get_equipos_by_id(id_equipo)

    if not equipo:
        raise ValueError(f"El equipo con ID {id_equipo} no existe.")

    nombre_equipo = request.form.get("nombre_equipo")
    lema_equipo = request.form.get("lema_equipo")
    maximo_miembros = request.form.get("maximo_miembros")
    color_equipo = request.form.get("color_equipo")
    estado_equipo = request.form.get("estado_equipo")
    id_comandante = request.form.get("id_comandante")

    equipos_services.update_equipo(
        id_equipo,
        nombre_equipo,
        lema_equipo,
        maximo_miembros,
        color_equipo,
        estado_equipo,
        id_comandante,
    )

    return redirect(url_for("equipo.index"))


@equipos_bp.route("/delete/<int:id_equipo>")
@permission_required(*Profiles.ROOT)
def delete(id_equipo):

    equipos_services.delete_equipo(id_equipo)

    return redirect(url_for("equipo.index"))


@equipos_bp.route("/<int:id_equipo>/manage")
def manage_members(id_equipo):
    context = dashboard_service.get_dashboard_data(request.path)
    equipo = equipos_services.get_equipos_by_id(id_equipo)

    if not equipo:
        # Manejar el caso de que el equipo no exista
        return "Equipo no encontrado", 404

    # Sobrescribimos el contexto genérico con datos específicos para esta página.
    # Esto asegura que el título y el breadcrumb en el layout principal sean correctos.
    context["page_title"] = f"MANAGE: {equipo.nombre_equipo.upper()}"
    context["page_data"] = f"SQUAD_ROSTER / {equipo.nombre_equipo.upper()}"

    # --- LÓGICA DE PAGINACIÓN ---
    # 1. Obtener el número de página de la URL (por defecto 1)
    page = request.args.get("page", 1, type=int)
    per_page = 5  # Cantidad fija de usuarios por página

    # 2. Identificar a quiénes excluir (los que ya son miembros)
    member_ids = {miembro.id_usuario for miembro in equipo.miembros}

    # 3. Pedir al servicio los usuarios paginados
    available_users, total_users = usuarios_services.get_available_users_paginated(
        member_ids, page, per_page
    )

    # 4. Calcular el total de páginas
    total_pages = math.ceil(total_users / per_page)

    return render_template(
        "dashboard/manage_equipo.html",
        equipo=equipo,
        usuarios_disponibles=available_users,
        current_page=page,
        per_page=per_page,
        total_pages=total_pages,
        total_users=total_users,
        **context,
    )


@equipos_bp.route("/<int:id_equipo>/add_member", methods=["POST"])
def add_member(id_equipo):
    id_usuario_a_anadir = request.form.get("id_usuario")
    if id_usuario_a_anadir:
        equipos_services.add_member_to_equipo(id_equipo, id_usuario_a_anadir)
    # Redirigimos de vuelta a la página de gestión para ver el cambio
    return redirect(url_for("equipo.manage_members", id_equipo=id_equipo))


@equipos_bp.route("/<int:id_equipo>/remove_member/<int:id_usuario>")
def remove_member(id_equipo, id_usuario):
    equipos_services.remove_member_from_equipo(id_equipo, id_usuario)
    return redirect(url_for("equipo.manage_members", id_equipo=id_equipo))
