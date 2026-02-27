"""Servicio de juegos - Catálogo de videojuegos disponibles.

Gestiona el CRUD de la entidad `Juego`, que contiene metadatos como nombre,
motor, género, estado y color (para UI). Este servicio garantiza que los
controladores nunca manipulen la sesión directamente y que todas las
validaciones se realicen de manera centralizada.
"""

from typing import Optional, List
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from app.db import session
from app import Juego


# --- CONSTANTES DE ERROR ---
ERROR_GAME_NOT_FOUND = "Juego no encontrado"
ERROR_NAME_REQUIRED = "El nombre del juego es obligatorio"
ERROR_INVALID_INPUT = "Dato de entrada inválido"
ERROR_DATABASE = "Error en la base de datos"


# --- CONSULTAS (READ) ---

def get_all_games() -> List[Juego]:
    """Retorna todos los juegos registrados."""
    try:
        current_app.logger.debug("Obteniendo todos los juegos")
        juegos = session.query(Juego).all()
        current_app.logger.debug(f"{len(juegos)} juegos encontrados")
        return juegos
    except SQLAlchemyError as e:
        current_app.logger.exception(f"Error obteniendo juegos: {e}")
        raise


def get_game_by_id(_id_juego: int) -> Optional[Juego]:
    """Busca un juego por su ID."""
    try:
        return session.query(Juego).filter_by(id_juego=_id_juego).first()
    except SQLAlchemyError as e:
        current_app.logger.exception(f"Error buscando juego {_id_juego}: {e}")
        raise


# --- MODIFICACIONES (CREATE/UPDATE/DELETE) ---

def create_game(
    nombre: str,
    motor: str,
    genero: str,
    estado: str,
    color: str,
) -> Juego:
    """Crea un nuevo juego tras validar campos obligatorios."""
    try:
        if not nombre:
            raise ValueError(ERROR_NAME_REQUIRED)

        current_app.logger.info(f"Creando juego '{nombre}'")
        nuevo = Juego(
            nombre_juego=nombre,
            motor_juego=motor,
            genero_juego=genero,
            estado_juego=estado,
            color_juego=color,
        )
        session.add(nuevo)
        session.commit()
        return nuevo
    except ValueError:
        raise
    except SQLAlchemyError as e:
        session.rollback()
        current_app.logger.exception(f"Error creando juego: {e}")
        raise


def update_game(
    id_juego: int,
    nombre: Optional[str] = None,
    motor: Optional[str] = None,
    genero: Optional[str] = None,
    estado: Optional[str] = None,
    color: Optional[str] = None,
) -> Juego:
    """Actualiza los campos proporcionados de un juego existente."""
    try:
        juego = get_game_by_id(id_juego)
        if not juego:
            raise ValueError(ERROR_GAME_NOT_FOUND)

        current_app.logger.info(f"Actualizando juego ID={id_juego}")
        if nombre is not None:
            juego.nombre_juego = nombre
        if motor is not None:
            juego.motor_juego = motor
        if genero is not None:
            juego.genero_juego = genero
        if estado is not None:
            juego.estado_juego = estado
        if color is not None:
            juego.color_juego = color

        session.commit()
        return juego
    except ValueError:
        raise
    except SQLAlchemyError as e:
        session.rollback()
        current_app.logger.exception(f"Error actualizando juego {id_juego}: {e}")
        raise


def delete_game(id_juego: int) -> bool:
    """Elimina un juego por ID."""
    try:
        juego = get_game_by_id(id_juego)
        if not juego:
            raise ValueError(ERROR_GAME_NOT_FOUND)
        current_app.logger.info(f"Eliminando juego ID={id_juego}")
        session.delete(juego)
        session.commit()
        return True
    except ValueError:
        raise
    except SQLAlchemyError as e:
        session.rollback()
        current_app.logger.exception(f"Error eliminando juego {id_juego}: {e}")
        raise