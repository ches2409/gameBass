from flask import Blueprint, request, render_template, redirect, url_for

from app.enums.tipos import CodigoProtocolo, CategoriaProtocolo
from app.services import protocolos_services, dashboard_service
from app.utils.decorators import permission_required
from app.utils.permissions import Profiles

protocolo_bp = Blueprint("protocolo", __name__, url_prefix="/protocolos")


@protocolo_bp.route("", strict_slashes=False)
@protocolo_bp.route("/", strict_slashes=False)
def index():
    protocolos = protocolos_services.get_all_protocols()

    context = dashboard_service.get_dashboard_data(request.path)

    return render_template(
        "dashboard/protocolos.html",
        protocolos=protocolos,
        codigos_listado=CodigoProtocolo,
        categorias_listado=CategoriaProtocolo,
        **context
    )


@protocolo_bp.route("/create", methods=["GET", "POST"], strict_slashes=False)
@permission_required(*Profiles.ROOT)
def create():
    if request.method == "POST":
        codigo_protocolo_txt = request.form.get("codigo_de_protocolo")
        nombre_protocolo = request.form["nombre_de_protocolo"]
        categoria_protocolo_txt = request.form.get("categoria_de_protocolo")
        descripcion_protocolo = request.form.get("descripcion_de_protocolo")

        codigo_protocolo = next(
            (e for e in CodigoProtocolo if e.codigo == codigo_protocolo_txt), None
        )

        categoria_protocolo = next(
            (e for e in CategoriaProtocolo if e.name == categoria_protocolo_txt), None
        )

        # Validación de seguridad: Si codigo_protocolo es válido, usamos su capacidad.
        if codigo_protocolo:
            descripcion_protocolo = codigo_protocolo.capacidad
        else:
            descripcion_protocolo = request.form.get("descripcion_de_protocolo")

        if protocolos_services.create_protocol(
            codigo_protocolo,
            nombre_protocolo,
            categoria_protocolo,
            descripcion_protocolo,
        ):
            return redirect(url_for("protocolo.index"))

    return render_template(
        "dashboard/protocolos/create.html",
        codigos_listado=CodigoProtocolo,
        categorias_listado=CategoriaProtocolo,
    )


@protocolo_bp.route(
    "/update/<int:id_protocolo>", methods=["GET", "POST"], strict_slashes=False
)
@permission_required(*Profiles.ROOT)
def update(id_protocolo):
    if request.method == "POST":
        codigo_protocolo_txt = request.form.get("codigo_de_protocolo")
        nombre_protocolo = request.form.get("nombre_de_protocolo")
        categoria_protocolo_txt = request.form.get("categoria_de_protocolo")
        descripcion_protocolo = request.form.get("descripcion_de_protocolo")

        codigo_protocolo = next(
            (e for e in CodigoProtocolo if e.codigo == codigo_protocolo_txt), None
        )

        categoria_protocolo = next(
            (e for e in CategoriaProtocolo if e.name == categoria_protocolo_txt), None
        )

        # Validación de seguridad: Evita crash si codigo_protocolo es None
        if codigo_protocolo:
            descripcion_protocolo = codigo_protocolo.capacidad
        else:
            descripcion_protocolo = request.form.get("descripcion_de_protocolo")

        protocolos_services.update_protocol(
            id_protocolo,
            codigo_protocolo,
            nombre_protocolo,
            categoria_protocolo,
            descripcion_protocolo,
        )

        return redirect(url_for("protocolo.index"))

    return render_template(
        "dashboard/protocolos/update.html",
        codigos_listado=CodigoProtocolo,
        categorias_listado=CategoriaProtocolo,
    )


@protocolo_bp.route("/delete/<int:id_protocolo>", strict_slashes=False)
@permission_required(*Profiles.ROOT)
def delete(id_protocolo):

    protocolos_services.delete_protocolo(id_protocolo)

    return redirect(url_for("protocolo.index"))
