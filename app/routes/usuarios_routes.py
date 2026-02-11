from flask import Blueprint, request, render_template, redirect, url_for

from app.services import dashboard_service, usuarios_services, jerarquias_services

usuarios_bp=Blueprint('usuario', __name__, url_prefix='/usuarios')

@usuarios_bp.route('/')
def index():
    
    context=dashboard_service.get_dashboard_data(request.path)
    usuarios_list=usuarios_services.get_all_usuarios()
    jerarquias_list=jerarquias_services.get_all_jerarquias()
    
    return render_template(
        'dashboard/usuarios.html',
        usuarios=usuarios_list,
        jerarquias_list=jerarquias_list,
        **context
    )

@usuarios_bp.route('/create', methods=['POST'])
def create():
    
    alias_usuario = request.form.get('alias_usuario')
    email_usuario = request.form.get('email_usuario')
    password_usuario = request.form.get('password_usuario')
    id_jerarquia = request.form.get('id_jerarquia')
    
    usuarios_services.create_usuario(alias_usuario, email_usuario,password_usuario, id_jerarquia)
    
    return redirect(url_for('usuario.index'))

@usuarios_bp.route('/update/<int:id_usuario>', methods=['POST'])
def update(id_usuario):
    
    usuario=usuarios_services.get_usuarios_by_id(id_usuario)
    
    if not usuario:
        raise ValueError(f"El usuario con ID {id_usuario} no existe.")

    alias_usuario = request.form.get('alias_usuario')
    email_usuario = request.form.get('email_usuario')
    password_usuario = request.form.get('password_usuario')
    id_jerarquia = request.form.get('id_jerarquia')
    
    usuarios_services.update_usuario(id_usuario, alias_usuario, email_usuario,password_usuario, id_jerarquia)
    
    return redirect(url_for('usuario.index'))

@usuarios_bp.route('/delete/<int:id_usuario>')
def delete(id_usuario):
    
    usuarios_services.delete_usuario(id_usuario)
    
    return redirect(url_for('usuario.index'))