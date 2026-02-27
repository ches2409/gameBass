"""Servicio de torneos - Administración de eventos competitivos.

Agrupa la lógica CRUD para los torneos que se organizan en la plataforma.

Funciones principales:
- Listar todos los torneos, con sus juegos y registros precargados
- Consultar un torneo por ID
- Crear, actualizar (parcial) y eliminar torneos
- Validaciones de entrada, conversiones de tipos y manejo de estados
- Manejo transaccional y logging adecuado

El modelo de negocio impone reglas específicas: las fechas deben ser ISO,
los niveles de acceso son enteros, y el estado debe ser uno de los valores
enum `EstadoTorneo`.
"""

from datetime import datetime
from typing import Optional, List
from flask import current_app
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.exc import SQLAlchemyError

from app.db import session
from app import Torneo
from app.enums.tipos import EstadoTorneo


# --- CONSTANTES DE ERROR ---
ERROR_TORNEO_NOT_FOUND = "Torneo no encontrado"
ERROR_REQUIRED_FIELDS = "Todos los campos son obligatorios"
ERROR_INVALID_DATE = "Fecha inválida, debe ser ISO-8601"
ERROR_INVALID_INPUT = "Dato de entrada inválido"
ERROR_DATABASE = "Error en la base de datos"


# --- CONSULTAS (READ) ---

def get_all_torneos() -> List[Torneo]:
    """Retorna todos los torneos con juego y registros precargados."""
    try:
        current_app.logger.debug("Obteniendo todos los torneos")
        torneos = (
            session.query(Torneo)
            .options(joinedload(Torneo.juego), selectinload(Torneo.registros))
            .all()
        )
        current_app.logger.debug(f"{len(torneos)} torneos encontrados")
        return torneos
    except SQLAlchemyError as e:
        current_app.logger.exception(f"Error al listar torneos: {e}")
        raise


def get_torneo_by_id(id_torneo: int) -> Optional[Torneo]:
    """Obtiene un torneo por su ID."""
    try:
        return session.query(Torneo).filter_by(id_torneo=id_torneo).first()
    except SQLAlchemyError as e:
        current_app.logger.exception(f"Error buscando torneo {id_torneo}: {e}")
        raise


# --- MODIFICACIONES (CREATE/UPDATE/DELETE) ---

def create_torneo(
    nombre_torneo: str,
    recompensa_torneo: str,
    nivel_acceso_min: int,
    estado_torneo: str,
    max_competidores: int,
    fecha_inicio: str,
    fecha_fin: str,
    id_juego: int,
) -> Torneo:
    """Crea un nuevo torneo tras validar y convertir los parámetros."""
    try:
        if not all([
            nombre_torneo,
            recompensa_torneo,
            nivel_acceso_min,
            estado_torneo,
            max_competidores,
            fecha_inicio,
            fecha_fin,
            id_juego,
        ]):
            raise ValueError(ERROR_REQUIRED_FIELDS)

        # conversión de tipos
        try:
            fecha_inicio_dt = datetime.fromisoformat(fecha_inicio)
            fecha_fin_dt = datetime.fromisoformat(fecha_fin)
        except ValueError:
            raise ValueError(ERROR_INVALID_DATE)

        try:
            estado_enum = EstadoTorneo[estado_torneo]
            nivel_int = int(nivel_acceso_min)
            max_int = int(max_competidores)
            juego_int = int(id_juego)
        except (KeyError, ValueError) as e:
            raise ValueError(f"{ERROR_INVALID_INPUT}: {e}")

        current_app.logger.info(f"Creando torneo '{nombre_torneo}'")

        nuevo = Torneo(
            nombre_torneo=nombre_torneo,
            recompensa_torneo=recompensa_torneo,
            nivel_acceso_min=nivel_int,
            estado_torneo=estado_enum,
            max_competidores=max_int,
            fecha_inicio=fecha_inicio_dt,
            fecha_fin=fecha_fin_dt,
            id_juego=juego_int,
        )
        session.add(nuevo)
        session.commit()
        return nuevo
    except ValueError:
        raise
    except SQLAlchemyError as e:
        session.rollback()
        current_app.logger.exception(f"Error creando torneo: {e}")
        raise


def update_torneo(
    id_torneo: int,
    nombre_torneo: Optional[str] = None,
    recompensa_torneo: Optional[str] = None,
    nivel_acceso_min: Optional[int] = None,
    estado_torneo: Optional[str] = None,
    max_competidores: Optional[int] = None,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
    id_juego: Optional[int] = None,
) -> Torneo:
    """Actualiza un torneo existente (solo campos no None)."""
    try:
        torneo = get_torneo_by_id(id_torneo)
        if not torneo:
            raise ValueError(ERROR_TORNEO_NOT_FOUND)

        current_app.logger.info(f"Actualizando torneo ID={id_torneo}")

        if nombre_torneo is not None:
            torneo.nombre_torneo = nombre_torneo
        if recompensa_torneo is not None:
            torneo.recompensa_torneo = recompensa_torneo
        if nivel_acceso_min is not None:
            torneo.nivel_acceso_min = int(nivel_acceso_min)
        if estado_torneo is not None:
            torneo.estado_torneo = EstadoTorneo[estado_torneo]
        if max_competidores is not None:
            torneo.max_competidores = int(max_competidores)
        if fecha_inicio is not None:
            torneo.fecha_inicio = datetime.fromisoformat(fecha_inicio)
        if fecha_fin is not None:
            torneo.fecha_fin = datetime.fromisoformat(fecha_fin)
        if id_juego is not None:
            torneo.id_juego = int(id_juego)

        session.commit()
        return torneo
    except ValueError:
        raise
    except SQLAlchemyError as e:
        session.rollback()
        current_app.logger.exception(f"Error actualizando torneo {id_torneo}: {e}")
        raise


def delete_torneo(id_torneo: int) -> bool:
    """Elimina un torneo si existe."""
    try:
        torneo = get_torneo_by_id(id_torneo)
        if not torneo:
            raise ValueError(ERROR_TORNEO_NOT_FOUND)
        current_app.logger.info(f"Eliminando torneo ID={id_torneo}")
        session.delete(torneo)
        session.commit()
        return True
    except ValueError:
        raise
    except SQLAlchemyError as e:
        session.rollback()
        current_app.logger.exception(f"Error eliminando torneo {id_torneo}: {e}")
        raise
