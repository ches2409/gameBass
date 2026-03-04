"""Servicio de registros - Manejo de puntuaciones, roles y equipos.

Este módulo contiene la lógica de negocio asociada con la tabla de
`registros` (puntajes). Provee:

- Búsqueda de registros (todos, recientes, por ID)
- Creación/actualización/eliminación de registros
- Validaciones de integridad (puntaje no negativo, existencia de FK)
- Verificación de que el usuario pertenece al equipo si se especifica uno
- Carga optimizada de relaciones para evitar N+1 queries
- Manejo transaccional y logging detallado

Las rutas de Flask deben llamar únicamente a estas funciones y nunca
manipular directamente la sesión o los modelos.
"""

from typing import Optional, List, Tuple
from flask import current_app
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.exc import SQLAlchemyError

from app.db import session
from app import Registro, Usuario, Equipo, Torneo, Juego, Rol

# --- CONSTANTES DE ERROR ---
ERROR_REGISTRO_NOT_FOUND = "Registro no encontrado"
ERROR_REQUIRED_FIELDS = "Puntaje, torneo, juego, usuario y rol son campos obligatorios"
ERROR_INVALID_SCORE = "El puntaje debe ser un número entero no negativo"
ERROR_USER_NOT_IN_TEAM = "El usuario no es miembro activo del equipo especificado"
ERROR_INVALID_INPUT = "Dato de entrada inválido"
ERROR_DATABASE = "Error en la base de datos"


# --- FUNCIONES DE CONSULTA (READ) ---


def get_all_registros() -> List[Registro]:
    """Retorna todos los registros con relaciones precargadas.

    Se cargan torneo y usuario (junto con su jerarquía) para evitar consultas
    adicionales al iterar.

    Returns:
        List[Registro]: todos los registros existentes.

    Raises:
        SQLAlchemyError: si ocurre un error en la base de datos.
    """
    try:
        current_app.logger.debug("Buscando todos los registros")
        registros = (
            session.query(Registro)
            .options(
                selectinload(Registro.torneo),
                selectinload(Registro.usuario).joinedload(Usuario.jerarquia),
            )
            .all()
        )
        current_app.logger.debug(f"Encontrados {len(registros)} registros")
        return registros
    except SQLAlchemyError as e:
        current_app.logger.exception(f"Error al obtener registros: {e}")
        raise


def get_recent_registros(limit: int = 10) -> List[Registro]:
    """Devuelve los últimos `limit` registros ordenados por ID descendente.

    Args:
        limit: cantidad máxima de registros a retornar (default 10).

    Returns:
        List[Registro]: lista de registros recientes.

    Raises:
        SQLAlchemyError: si ocurre un error en la consulta.
    """
    try:
        current_app.logger.debug(f"Buscando {limit} registros recientes")
        registros = (
            session.query(Registro)
            .options(
                selectinload(Registro.torneo),
                selectinload(Registro.usuario).joinedload(Usuario.jerarquia),
            )
            .order_by(Registro.id_registro.desc())
            .limit(limit)
            .all()
        )
        return registros
    except SQLAlchemyError as e:
        current_app.logger.exception(f"Error al obtener registros recientes: {e}")
        raise


def get_registro_by_id(id_registro: int) -> Optional[Registro]:
    """Retorna un registro por su ID.

    Args:
        id_registro: ID del registro buscado.

    Returns:
        Optional[Registro]: el registro si existe, sino None.

    Raises:
        SQLAlchemyError: en caso de error de base de datos.
    """
    try:
        current_app.logger.debug(f"Buscando registro ID={id_registro}")
        registro = (
            session.query(Registro)
            .options(
                selectinload(Registro.torneo),
                selectinload(Registro.usuario).joinedload(Usuario.jerarquia),
            )
            .filter_by(id_registro=id_registro)
            .first()
        )
        return registro
    except SQLAlchemyError as e:
        current_app.logger.exception(f"Error al buscar registro {id_registro}: {e}")
        raise


# --- FUNCIONES DE MODIFICACIÓN (CREATE/UPDATE/DELETE) ---


def create_registro(
    puntaje: int,
    id_torneo: int,
    id_juego: int,
    id_usuario: int,
    id_rol: int,
    id_equipo: Optional[int] = None,
) -> Registro:
    """Crea un nuevo registro con validaciones completas.

    Args:
        puntaje: puntuación obtenida (>=0).
        id_torneo: ID del torneo donde se registró el puntaje.
        id_juego: ID del juego correspondiente.
        id_usuario: ID del usuario que hizo el registro.
        id_rol: ID del rol jugado.
        id_equipo: ID del equipo (opcional).

    Returns:
        Registro: el objeto recién creado con PK asignado.

    Raises:
        ValueError: si falta un campo obligatorio o la validación falla.
        SQLAlchemyError: si ocurre un error al persistir en la base.
    """
    try:
        # campos obligatorios
        if any(v is None for v in [puntaje, id_torneo, id_juego, id_usuario, id_rol]):
            raise ValueError(ERROR_REQUIRED_FIELDS)

        # puntaje válido
        if not isinstance(puntaje, int) or puntaje < 0:
            raise ValueError(ERROR_INVALID_SCORE)

        # convertir IDs a int y comprobar existencia de FK
        try:
            id_torneo = int(id_torneo)
            id_juego = int(id_juego)
            id_usuario = int(id_usuario)
            id_rol = int(id_rol)
        except (TypeError, ValueError) as e:
            raise ValueError(f"{ERROR_INVALID_INPUT}: {e}")

        if not session.get(Torneo, id_torneo):
            raise ValueError("Torneo no encontrado")
        if not session.get(Juego, id_juego):
            raise ValueError("Juego no encontrado")
        usuario = session.get(Usuario, id_usuario)
        if not usuario:
            raise ValueError("Usuario no encontrado")
        if not session.get(Rol, id_rol):
            raise ValueError("Rol no encontrado")

        # validación de equipo/miembro
        if id_equipo is not None:
            id_equipo = int(id_equipo)
            es_miembro = any(e.id_equipo == id_equipo for e in usuario.membresias)
            if not es_miembro:
                raise ValueError(ERROR_USER_NOT_IN_TEAM)

        current_app.logger.info(
            f"Creando registro: usuario={id_usuario} torneo={id_torneo} puntaje={puntaje}"
        )

        nuevo = Registro(
            puntaje=puntaje,
            id_torneo=id_torneo,
            id_juego=id_juego,
            id_usuario=id_usuario,
            id_rol=id_rol,
            id_equipo=id_equipo,
        )
        session.add(nuevo)
        session.commit()
        return nuevo

    except ValueError:
        raise
    except SQLAlchemyError as e:
        session.rollback()
        current_app.logger.exception(f"Error creando registro: {e}")
        raise


def update_registro() -> Registro:
    pass


def delete_registro(id_registro: int) -> bool:
    """Elimina un registro por su ID.

    Args:
        id_registro: ID del registro a borrar.

    Returns:
        bool: True si se eliminó correctamente.

    Raises:
        ValueError: si el registro no existe.
        SQLAlchemyError: error de base de datos.
    """
    try:
        registro = get_registro_by_id(id_registro)
        if not registro:
            raise ValueError(ERROR_REGISTRO_NOT_FOUND)

        current_app.logger.info(f"Eliminando registro ID={id_registro}")
        session.delete(registro)
        session.commit()
        return True
    except ValueError:
        raise
    except SQLAlchemyError as e:
        session.rollback()
        current_app.logger.exception(f"Error eliminando registro {id_registro}: {e}")
        raise
