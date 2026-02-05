from flask import Blueprint, request, render_template, redirect, url_for

from app.enums.tipos import EstadoJuego
from app.services import dashboard_service, juegos_services

juegos_bp = Blueprint('juego', __name__, url_prefix='/juegos')

@juegos_bp.route('/')
def index():
    
    # Obtener los datos generales del dashboard
    context = dashboard_service.get_dashboard_data(request.path)
    
    # Obtener la lista de todos los juegos
    juegos_list = juegos_services.get_all_games()
    
    # Enviar todo al HTML
    return render_template(
        'dashboard/juegos.html',
        estados=EstadoJuego,
        juegos=juegos_list,
        **context
    )

@juegos_bp.route('/create', methods=['POST'])
def create():
        
    # Obtener los datos simples del formulario
    nombre = request.form.get('nombre_de_juego')
    motor = request.form.get('motor_de_juego')
    genero = request.form.get('genero_de_juego')
    estado = request.form.get('estado_de_juego')
    color = request.form.get('color_de_juego')
    
    # Crear el nuevo juego
    juegos_services.create_game(nombre, motor, genero, estado, color)
    
    
    return redirect(url_for('juego.index'))

@juegos_bp.route('/update/<int:id_juego>', methods=['POST'])
def update(id_juego):
    # Obtener los datos del formulario de actualización
    nombre = request.form.get('nombre_de_juego')
    motor = request.form.get('motor_de_juego')
    genero = request.form.get('genero_de_juego')
    estado = request.form.get('estado_de_juego')
    color = request.form.get('color_de_juego')

    # Llamar al servicio para actualizar el juego
    juegos_services.update_game(id_juego, nombre, motor, genero, estado, color)

    # Redirigir a la página principal de juegos
    return redirect(url_for('juego.index'))

@juegos_bp.route('/delete/<int:id_juego>')
def delete(id_juego):
    # Llamar al servicio para eliminar el juego
    juegos_services.delete_game(id_juego)

    # Redirigir a la página principal de juegos
    return redirect(url_for('juego.index'))
