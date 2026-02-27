"""Servicio de roles - Gestión de perfiles/funciones dentro de GameBass.

Permite administrar los roles que pueden asignarse a usuarios. Se asegura de
que no existan duplicados y centraliza la lógica de consulta y modificación.
"""

from typing import Optional, List
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from app.db import session
from app.models.roles_models import Rol


# --- CONSTANTES DE ERROR ---
ERROR_ROLE_NOT_FOUND = "Rol no encontrado"
ERROR_NAME_REQUIRED = "El nombre del rol es obligatorio"
ERROR_ROLE_ALREADY_EXISTS = "El rol ya existe"
ERROR_INVALID_INPUT = "Dato de entrada inválido"
ERROR_DATABASE = "Error en la base de datos"


# --- CONSULTAS (READ) ---

def get_all_roles() -> List[Rol]:
    """Retorna todos los roles disponibles."""
    try:
        current_app.logger.debug("Obteniendo todos los roles")
        roles = session.query(Rol).all()
        current_app.logger.debug(f"{len(roles)} roles encontrados")
        return roles
    except SQLAlchemyError as e:
        current_app.logger.exception(f"Error obteniendo roles: {e}")
        raise


def get_roles_by_id(id_rol: int) -> Optional[Rol]:
    """Busca un rol por su ID."""
    try:
        return session.query(Rol).get(id_rol)
    except SQLAlchemyError as e:
        current_app.logger.exception(f"Error buscando rol {id_rol}: {e}")
        raise


# --- MODIFICACIONES ---

def create_rol(nombre: str, descripcion_rol: str, especialidad_rol: str) -> Rol:
    """Crea un nuevo rol, evitando duplicados."""
    try:
        if not nombre:
            raise ValueError(ERROR_NAME_REQUIRED)

        # verificar unicidad
        existing = session.query(Rol).filter_by(nombre_rol=nombre).first()
        if existing:
            raise ValueError(ERROR_ROLE_ALREADY_EXISTS)

        current_app.logger.info(f"Creando rol '{nombre}'")
        new_rol = Rol(
            nombre_rol=nombre,
            descripcion_rol=descripcion_rol,
            especialidad_rol=especialidad_rol,
        )
        session.add(new_rol)
        session.commit()
        return new_rol
    except ValueError:
        raise
    except SQLAlchemyError as e:
        session.rollback()
        current_app.logger.exception(f"Error creando rol: {e}")
        raise


def update_rol(
    id_rol: int,
    nombre_rol: Optional[str] = None,
    descripcion_rol: Optional[str] = None,
    especialidad_rol: Optional[str] = None,
) -> Rol:
    """Actualiza los campos de un rol existente."""
    try:
        rol = get_roles_by_id(id_rol)
        if not rol:
            raise ValueError(ERROR_ROLE_NOT_FOUND)

        current_app.logger.info(f"Actualizando rol ID={id_rol}")
        if nombre_rol is not None:
            rol.nombre_rol = nombre_rol
        if descripcion_rol is not None:
            rol.descripcion_rol = descripcion_rol
        if especialidad_rol is not None:
            rol.especialidad_rol = especialidad_rol

        session.commit()
        return rol
    except ValueError:
        raise
    except SQLAlchemyError as e:
        session.rollback()
        current_app.logger.exception(f"Error actualizando rol {id_rol}: {e}")
        raise


def delete_rol(id_rol: int) -> bool:
    """Elimina un rol por su ID."""
    try:
        rol = get_roles_by_id(id_rol)
        if not rol:
            raise ValueError(ERROR_ROLE_NOT_FOUND)
        current_app.logger.info(f"Eliminando rol ID={id_rol}")
        session.delete(rol)
        session.commit()
        return True
    except ValueError:
        raise
    except SQLAlchemyError as e:
        session.rollback()
        current_app.logger.exception(f"Error eliminando rol {id_rol}: {e}")
        raise