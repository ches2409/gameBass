from flask import Blueprint, request, render_template, redirect, url_for, current_app
from werkzeug.utils import secure_filename
import os
import time
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
    avatar_url=request.form.get('avatar_url')
    avatar_file = request.files.get('avatar_file')
    foto_final = None # Empezamos sin foto
    
    # REGLA DE PRIORIDAD: El archivo subido tiene prioridad sobre la URL.
    if avatar_file and avatar_file.filename != '':
        filename = secure_filename(avatar_file.filename)
        # Creamos un nombre único para evitar colisiones
        unique_filename = f"avatar_{int(time.time())}_{filename}"
        save_path = os.path.join(current_app.static_folder, 'uploads/avatars', unique_filename)
        avatar_file.save(save_path)
        foto_final = unique_filename # Guardamos solo el nombre del archivo
    elif 'avatar_url' in request.form: # Si no hay archivo, usamos la URL (incluso si está vacía para borrar)
        foto_final = avatar_url
    
    usuarios_services.create_usuario(alias_usuario, email_usuario,password_usuario, foto_final, id_jerarquia)
    
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
    avatar_url = request.form.get("avatar_url")
    avatar_file = request.files.get('avatar_file')
    foto_final = None # Por defecto, no cambiamos la foto
    
    # REGLA DE PRIORIDAD: El archivo subido tiene prioridad sobre la URL.
    if avatar_file and avatar_file.filename != '':
        filename = secure_filename(avatar_file.filename)
        # Usamos el ID de usuario y el tiempo para garantizar un nombre de archivo único
        unique_filename = f"avatar_{id_usuario}_{int(time.time())}_{filename}"
        save_path = os.path.join(current_app.static_folder, 'uploads/avatars', unique_filename)
        avatar_file.save(save_path)
        foto_final = unique_filename
    elif 'avatar_url' in request.form:
        # Si el campo URL fue enviado (incluso vacío), respetamos ese valor para permitir borrar la foto.
        foto_final = avatar_url

    usuarios_services.update_usuario(id_usuario, alias_usuario, email_usuario,password_usuario,foto_final, id_jerarquia)

    return redirect(url_for('usuario.index'))

@usuarios_bp.route('/delete/<int:id_usuario>')
def delete(id_usuario):
    
    usuarios_services.delete_usuario(id_usuario)
    
    return redirect(url_for('usuario.index'))
