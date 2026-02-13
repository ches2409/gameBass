from flask import Blueprint, request, render_template, redirect, url_for

from app.enums.tipos import EstadoEquipo
from app.services import dashboard_service, equipos_services, usuarios_services

equipos_bp = Blueprint('equipo', __name__, url_prefix='/equipos')

@equipos_bp.route('/')
def index():
    context = dashboard_service.get_dashboard_data(request.path)
    equipos_list = equipos_services.get_all_equipos()
    usuarios_list = usuarios_services.get_all_usuarios()
    
    return render_template(
        'dashboard/equipos.html',
        estados_equipo=EstadoEquipo,
        equipos=equipos_list,
        usuarios=usuarios_list,
        **context
    )

@equipos_bp.route('/create', methods=['POST'])
def create():
    
    nombre_equipo = request.form.get('nombre_equipo')
    lema_equipo = request.form.get('lema_equipo')
    color_equipo = request.form.get('color_equipo')
    estado_equipo = request.form.get('estado_equipo')
    id_comandante = request.form.get('id_comandante')
    
    equipos_services.create_equipo(nombre_equipo, lema_equipo,color_equipo, estado_equipo, id_comandante)
    
    return redirect(url_for('equipo.index'))

@equipos_bp.route('/update/<int:id_equipo>', methods=['POST'])
def update(id_equipo):
    
    equipo= equipos_services.get_equipos_by_id(id_equipo)
    
    if not equipo:
        raise ValueError(f"El equipo con ID {id_equipo} no existe.")
    
    
    nombre_equipo = request.form.get('nombre_equipo')
    lema_equipo = request.form.get('lema_equipo')
    color_equipo = request.form.get('color_equipo')
    estado_equipo = request.form.get('estado_equipo')
    id_comandante = request.form.get('id_comandante')
    
    equipos_services.update_equipo(id_equipo, nombre_equipo, lema_equipo, color_equipo, estado_equipo, id_comandante)
    
    return redirect(url_for('equipo.index'))

@equipos_bp.route('/delete/<int:id_equipo>')
def delete(id_equipo):
    
    equipos_services.delete_equipo(id_equipo)
    
    return redirect(url_for('equipo.index'))
