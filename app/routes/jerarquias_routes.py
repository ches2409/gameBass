from flask import Blueprint, render_template, request, redirect, url_for

from app.services import jerarquias_services, protocolos_services, dashboard_service
from app.utils.decorators import permission_required
from app.utils.permissions import Profiles

jerarquia_bp = Blueprint("jerarquia", __name__, url_prefix="/jerarquias")


@jerarquia_bp.route("/", strict_slashes=False)
def index():
    """
    Paso 1: El Almacén.
    Aquí reunimos todo lo que la página necesita.
    1. Obtenemos los datos generales del dashboard.
    2. Obtenemos la lista de TODAS las jerarquías existentes.
    3. MUY IMPORTANTE: Obtenemos la lista de TODOS los protocolos.
       Esta lista la usaremos para construir nuestros 'tags' seleccionables.
    """
    context = dashboard_service.get_dashboard_data(request.path)
    jerarquias = jerarquias_services.get_all_jerarquias()
    protocolos = protocolos_services.get_all_protocols()

    # 4. Enviamos todo al HTML. 'protocolos_listado' será el nombre que usaremos en el template.
    return render_template(
        "dashboard/jerarquias.html",
        jerarquias=jerarquias,
        protocolos_listado=protocolos,
        **context
    )


@jerarquia_bp.route("/create", methods=["POST"])
@permission_required(*Profiles.SISTEMA)
def create():
    # Obtenemos los datos simples del formulario
    nombre = request.form.get("nombre_de_jerarquia")
    subtitulo = request.form.get("subtitulo_de_jerarquia")
    nivel = request.form.get("nivel_jerarquia")
    descripcion = request.form.get("descripcion_de_jerarquia")
    color = request.form.get("color_jerarquia")  # <-- ¡Aquí recogemos el color!

    # Obtenemos la LISTA de IDs de los protocolos que seleccionamos
    protocolos_ids = request.form.getlist("protocolos_ids")
    protocolos = [
        protocolos_services.get_protocolo_by_id(pid) for pid in protocolos_ids
    ]

    jerarquias_services.create_jerarquia(
        nombre, subtitulo, descripcion, nivel, protocolos, color
    )

    return redirect(url_for("jerarquia.index"))


@jerarquia_bp.route(
    "/update/<int:id_jerarquia>", methods=["POST"], strict_slashes=False
)
@permission_required(*Profiles.SISTEMA)
def update(id_jerarquia):
    nombre = request.form.get("nombre_de_jerarquia")
    subtitulo = request.form.get("subtitulo_de_jerarquia")
    nivel = request.form.get("nivel_jerarquia")
    descripcion = request.form.get("descripcion_de_jerarquia")
    protocolos_ids = request.form.getlist("protocolos_ids")
    color = request.form.get("color_jerarquia")

    # 1. Convertimos los IDs de los protocolos en los objetos que la BD espera (igual que en 'create')
    protocolos = [
        protocolos_services.get_protocolo_by_id(pid) for pid in protocolos_ids
    ]

    # 2. ¡AQUÍ ESTÁ EL ARREGLO! Pasamos 'descripcion' y 'nivel' en el orden correcto.
    jerarquias_services.update_jerarquia(
        id_jerarquia, nombre, subtitulo, descripcion, nivel, protocolos, color
    )

    return redirect(url_for("jerarquia.index"))


@jerarquia_bp.route("/delete/<int:id_jerarquia>", strict_slashes=False)
@permission_required(*Profiles.SISTEMA)
def delete(id_jerarquia):
    jerarquias_services.delete_jerarquia(id_jerarquia)
    return redirect(url_for("jerarquia.index"))
