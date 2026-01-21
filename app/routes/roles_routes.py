from flask import Blueprint, render_template, request, redirect, url_for
from app.services import roles_services
from app.enums.tipos import RolUsuario

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
    return render_template("dashboard/index.html", roles=roles)

@rol_bp.route('/create', methods=['GET', 'POST'] , strict_slashes=False)
def create():
    
    if request.method == 'POST':
        rol_nombre = request.form['nombre_de_rol']
        rol_descripcion = request.form['descripcion_de_rol']
        
        if roles_services.create_rol(rol_nombre, rol_descripcion):
            return redirect(url_for('roles.index'))
    # Pasamos el Enum para que sirva de sugerencia en el datalist
    return render_template("dashboard/create.html", roles_listado=RolUsuario)