from typing import Optional

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    current_app,
    flash,
)
from app.services import roles_services
from app.enums.tipos import RolUsuario, EspecialidadRol
from app.services import dashboard_service
from app.utils.decorators import permission_required
from app.utils.permissions import Permissions, Profiles

rol_bp = Blueprint("rol", __name__, url_prefix="/roles")


@rol_bp.route("", strict_slashes=False)
@rol_bp.route("/", strict_slashes=False)
def index() -> str:
    """Listado de roles.

    Carga todos los roles desde el servicio y añade el contexto del dashboard.
    """
    try:
        roles = roles_services.get_all_roles()
    except Exception as e:
        current_app.logger.exception("Error al obtener roles")
        roles = []

    # Obtener la configuración visual (Menú, Alertas, Métricas) del servicio
    context = dashboard_service.get_dashboard_data(request.path)

    return render_template(
        "dashboard/roles.html",
        roles=roles,
        especialidad_enum=EspecialidadRol,
        roles_listado=RolUsuario,
        **context,
    )


@rol_bp.route("/create", methods=["POST"], strict_slashes=False)
@permission_required(*Profiles.SISTEMA)
def create() -> redirect:
    """Crear un nuevo rol.

    Procesa el formulario POST para crear un nuevo rol. Valida que el nombre
    no esté vacío y busca la especialidad correspondiente. Si la especialidad
    existe en el Enum, usa su descripción predefinida; de lo contrario, usa
    la descripción proporcionada en el formulario.

    Returns:
        redirect: Redirección a la página de índice de roles.

    Flash messages:
        - "Rol creado correctamente." (success) si la creación fue exitosa.
        - "El nombre del rol es requerido." (danger) si el nombre está vacío.
        - "Error al crear el rol." (danger) si ocurre una excepción.
        - "No se pudo crear el rol." (warning) si create_rol retorna False.
    """
    rol_nombre = request.form.get("nombre_de_rol", "").strip()
    rol_especialidad_txt = request.form.get("especialidad_de_rol", "").strip()

    # Validaciones básicas
    if not rol_nombre:
        flash("El nombre del rol es requerido.", "danger")
        return redirect(url_for("rol.index"))

    # Buscar la especialidad por su título (si fue seleccionada)
    rol_especialidad: Optional[EspecialidadRol] = None
    if rol_especialidad_txt:
        rol_especialidad = next(
            (
                e
                for e in EspecialidadRol
                if getattr(e, "titulo", None) == rol_especialidad_txt
            ),
            None,
        )

    # Descripción: preferir la descripción del enum, si existe
    rol_descripcion = (
        rol_especialidad.descripcion
        if rol_especialidad
        else request.form.get("descripcion_de_rol", "").strip()
    )

    try:
        success = roles_services.create_rol(
            rol_nombre, rol_descripcion, rol_especialidad
        )
    except Exception as e:
        current_app.logger.exception("Error creando rol")
        flash("Error al crear el rol.", "danger")
        return redirect(url_for("rol.index"))

    if success:
        flash("Rol creado correctamente.", "success")
        return redirect(url_for("rol.index"))

    flash("No se pudo crear el rol.", "warning")
    return redirect(url_for("rol.index"))


@rol_bp.route("/update/<int:id_rol>", methods=["POST"], strict_slashes=False)
@permission_required(*Profiles.SISTEMA)
def update(id_rol: int) -> redirect:
    """Actualizar un rol existente.

    Procesa el formulario POST para actualizar los datos de un rol. Valida que
    el nombre del rol no esté vacío y busca la especialidad correspondiente.
    Si la especialidad existe en el Enum, usa su descripción predefinida.

    Args:
        id_rol (int): ID del rol a actualizar (capturado desde la URL).

    Returns:
        redirect: Redirección a la página de índice de roles.

    Flash messages:
        - "Rol actualizado correctamente." (success) si la actualización fue exitosa.
        - "El nombre del rol es requerido." (danger) si el nombre está vacío.
        - "Error al actualizar el rol." (danger) si ocurre una excepción.
    """
    nombre_rol = request.form.get("nombre_de_rol", "").strip()
    especialidad_rol_txt = request.form.get("especialidad_de_rol", "").strip()

    if not nombre_rol:
        flash("El nombre del rol es requerido.", "danger")
        return redirect(url_for("rol.index"))

    especialidad_rol = next(
        (
            e
            for e in EspecialidadRol
            if getattr(e, "titulo", None) == especialidad_rol_txt
        ),
        None,
    )

    descripcion_rol = (
        especialidad_rol.descripcion
        if especialidad_rol
        else request.form.get("descripcion_de_rol", "").strip()
    )

    try:
        roles_services.update_rol(id_rol, nombre_rol, descripcion_rol, especialidad_rol)
        flash("Rol actualizado correctamente.", "success")
    except Exception:
        current_app.logger.exception("Error actualizando rol")
        flash("Error al actualizar el rol.", "danger")

    return redirect(url_for("rol.index"))


@rol_bp.route("/delete/<int:id_rol>", strict_slashes=False, methods=["POST"])
@permission_required(*Profiles.SISTEMA)
def delete(id_rol: int) -> redirect:
    """Eliminar un rol del sistema.

    Procesa la eliminación de un rol. Solo acepta POST para evitar
    eliminaciones accidentales por GET. Captura excepciones y proporciona
    feedback al usuario mediante flash messages.

    Args:
        id_rol (int): ID del rol a eliminar (capturado desde la URL).

    Returns:
        redirect: Redirección a la página de índice de roles.

    Flash messages:
        - "Rol eliminado." (info) si la eliminación fue exitosa.
        - "No se pudo eliminar el rol." (danger) si ocurre una excepción.
    """
    try:
        roles_services.delete_rol(id_rol)
        flash("Rol eliminado.", "info")
    except Exception:
        current_app.logger.exception("Error eliminando rol")
        flash("No se pudo eliminar el rol.", "danger")

    return redirect(url_for("rol.index"))
