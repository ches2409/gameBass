from flask import Blueprint, render_template, request, redirect, url_for
from app.services import roles_services
from app.enums.tipos import RolUsuario, EspecialidadRol
from app.services import dashboard_service

rol_bp = Blueprint('roles', __name__, url_prefix='/roles')

@rol_bp.route('', strict_slashes=False)
@rol_bp.route('/', strict_slashes=False)
def index():
    try:
        roles = roles_services.get_all_roles()
    except Exception as e:
        # Si la tabla no existe, devolvemos una lista vacía o manejamos el error
        print(f"Error al obtener roles: {e}")
        roles = []
        
        

    # Obtener la configuración visual (Menú, Alertas, Métricas) del servicio
    context = dashboard_service.get_dashboard_data(request.path)

    return render_template('dashboard/roles.html', roles=roles, especialidad_enum=EspecialidadRol, **context)

@rol_bp.route('/create', methods=['GET', 'POST'] , strict_slashes=False)
def create():
    
    if request.method == 'POST':
        rol_nombre = request.form['nombre_de_rol']
        rol_especialidad_txt = request.form.get('especialidad_de_rol')
        
        # Buscamos el miembro del Enum que coincida con el título seleccionado en el input
        rol_especialidad = next((e for e in EspecialidadRol if e.titulo == rol_especialidad_txt), None)
        
        # Lógica para asignar la descripción:
        # Si encontramos la especialidad en el Enum, usamos su descripción predefinida.
        # De lo contrario, usamos lo que el usuario haya escrito en el formulario como respaldo.
        rol_descripcion = rol_especialidad.descripcion if rol_especialidad else request.form.get('descripcion_de_rol')

        # Pasamos los 3 argumentos que espera el servicio
        if roles_services.create_rol(rol_nombre, rol_descripcion, rol_especialidad):
            return redirect(url_for('roles.index'))
    # Pasamos el Enum para que sirva de sugerencia en el datalist
    return render_template("dashboard/create.html", roles_listado=RolUsuario, especialidad_enum=EspecialidadRol)