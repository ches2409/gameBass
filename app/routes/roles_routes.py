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
    return render_template("dashboard/roles/create.html", roles_listado=RolUsuario, especialidad_enum=EspecialidadRol)

@rol_bp.route('/update/<int:id_rol>', methods=['GET', 'POST'] , strict_slashes=False)
def update(id_rol):
    if request.method == 'POST':
        nombre_rol = request.form['nombre_de_rol']
        especialidad_rol_txt = request.form.get('especialidad_de_rol')
        
        # Convertimos el texto del input al objeto Enum correspondiente
        especialidad_rol = next((e for e in EspecialidadRol if e.titulo == especialidad_rol_txt), None)
        
        # Actualizamos la descripción basada en la especialidad seleccionada
        descripcion_rol = especialidad_rol.descripcion if especialidad_rol else request.form['descripcion_de_rol']
        
        roles_services.update_rol(id_rol, nombre_rol, descripcion_rol, especialidad_rol)
        
        return redirect(url_for('roles.index'))
    return render_template("dashboard/roles/update.html", roles_listado=RolUsuario, especialidad_enum=EspecialidadRol)

@rol_bp.route('/delete/<int:id_rol>', strict_slashes=False)
def delete(id_rol):
    roles_services.delete_rol(id_rol)
    
    return redirect(url_for('roles.index'))

