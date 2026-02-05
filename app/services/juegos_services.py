from app import Juego
from app.db import session


def get_all_games():
    return session.query(Juego).all()

def get_game_by_id(_id_juego):
    return session.query(Juego).filter_by(id_juego=_id_juego).first()

def create_game(nombre, motor, genero, estado, color):
    if not nombre:
        raise ValueError("El nombre del juego es obligatorio.")
    
    new_game = Juego(
        nombre_juego=nombre,
        motor_juego=motor,
        genero_juego=genero,
        estado_juego=estado,
        color_juego=color
    )
    
    session.add(new_game)
    session.commit()
    return new_game

def update_game(id_juego, nombre, motor, genero, estado, color):
    game = get_game_by_id(id_juego)
    
    if not game:
        raise ValueError(f"No se encontró el juego con id {id_juego}")

    # Actualizar los campos del objeto 'Juego' existente
    game.nombre_juego = nombre
    game.motor_juego = motor
    game.genero_juego = genero
    game.estado_juego = estado
    game.color_juego = color

    session.commit() # Guardar los cambios en la base de datos
    return game

def delete_game(id_juego):
    game = get_game_by_id(id_juego)
    if not game:
        raise ValueError(f"No se encontró el juego con id {id_juego}")

    session.delete(game)
    session.commit()