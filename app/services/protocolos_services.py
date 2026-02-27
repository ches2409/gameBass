from __future__ import annotations

from typing import List, Optional

from sqlalchemy.exc import SQLAlchemyError

from flask import current_app

from app.db import session
from app.models.protocolos_models import Protocolo


# ------------ mensajes de error constantes ------------
ERROR_PROTOCOLO_NO_EXISTE = "El protocolo con id={0} no existe."
ERROR_PROTOCOLO_DUPLICADO = "Ya existe un protocolo con nombre '{0}'."
ERROR_PROTOCOLO_NOMBRE_OBLIGATORIO = "El nombre del protocolo es obligatorio."


# ---------- funciones helper internas (no exportadas) ----------

def _check_nombre_unique(nombre: str, exclude_id: Optional[int] = None) -> bool:
    """Verifica que no exista otro protocolo con el mismo nombre.

    Si `exclude_id` se proporciona, se omite ese registro (usado en update).
    """
    query = session.query(Protocolo).filter_by(nombre_protocolo=nombre)
    if exclude_id is not None:
        query = query.filter(Protocolo.id_protocolo != exclude_id)
    return session.query(query.exists()).scalar() is False


# -------------------- API pública --------------------

def get_all_protocols() -> List[Protocolo]:
    """Retorna todos los protocolos existentes."""
    current_app.logger.debug("Consultando todos los protocolos")
    return session.query(Protocolo).all()


def get_protocolo_by_id(id_protocolo: int) -> Optional[Protocolo]:
    """Busca un protocolo por su clave primaria.

    Devuelve `None` si no se encuentra.
    """
    current_app.logger.debug("Buscando protocolo id=%s", id_protocolo)
    return session.query(Protocolo).filter_by(id_protocolo=id_protocolo).first()


def create_protocol(
    codigo_protocolo: str,
    nombre_protocolo: str,
    categoria_protocolo: str,
    descripcion_protocolo: Optional[str] = None,
) -> Protocolo:
    """Crea un nuevo protocolo.

    Lanza `ValueError` si falta el nombre o si ya existe.
    """
    if not nombre_protocolo:
        current_app.logger.warning("Nombre de protocolo vacío")
        raise ValueError(ERROR_PROTOCOLO_NOMBRE_OBLIGATORIO)

    if not _check_nombre_unique(nombre_protocolo):
        current_app.logger.warning("Nombre de protocolo duplicado: %s", nombre_protocolo)
        raise ValueError(ERROR_PROTOCOLO_DUPLICADO.format(nombre_protocolo))

    nuevo = Protocolo(
        codigo_protocolo=codigo_protocolo,
        nombre_protocolo=nombre_protocolo,
        categoria_protocolo=categoria_protocolo,
        descripcion_protocolo=descripcion_protocolo,
    )

    try:
        session.add(nuevo)
        session.commit()
        current_app.logger.info("Protocolo creado: %s", nuevo)
        return nuevo
    except SQLAlchemyError as e:  # noqa: F841 - variable utilizada en log
        session.rollback()
        current_app.logger.error("Error SQL al crear protocolo: %s", e)
        raise


def update_protocol(
    id_protocolo: int,
    codigo_protocolo: Optional[str] = None,
    nombre_protocolo: Optional[str] = None,
    categoria_protocolo: Optional[str] = None,
    descripcion_protocolo: Optional[str] = None,
) -> Protocolo:
    """Actualiza los campos de un protocolo existente.

    Cualquier parámetro `None` se ignora.
    Lanza `LookupError` si el protocolo no existe, `ValueError` si el
    nombre propuesto ya está en uso.
    """
    protocolo = get_protocolo_by_id(id_protocolo)
    if protocolo is None:
        current_app.logger.warning("Intento de actualizar protocolo inexistente %s", id_protocolo)
        raise LookupError(ERROR_PROTOCOLO_NO_EXISTE.format(id_protocolo))

    if nombre_protocolo and not _check_nombre_unique(nombre_protocolo, exclude_id=id_protocolo):
        current_app.logger.warning("Nombre duplicado en actualización: %s", nombre_protocolo)
        raise ValueError(ERROR_PROTOCOLO_DUPLICADO.format(nombre_protocolo))

    if codigo_protocolo is not None:
        protocolo.codigo_protocolo = codigo_protocolo
    if nombre_protocolo is not None:
        protocolo.nombre_protocolo = nombre_protocolo
    if categoria_protocolo is not None:
        protocolo.categoria_protocolo = categoria_protocolo
    if descripcion_protocolo is not None:
        protocolo.descripcion_protocolo = descripcion_protocolo

    try:
        session.commit()
        current_app.logger.info("Protocolo actualizado: %s", protocolo)
        return protocolo
    except SQLAlchemyError as e:
        session.rollback()
        current_app.logger.error("Error SQL al actualizar protocolo: %s", e)
        raise


def delete_protocolo(id_protocolo: int) -> bool:
    """Elimina un protocolo existente.

    Retorna `True` si la eliminación se realiza, lanza `LookupError` si no
    existe.
    """
    protocolo = get_protocolo_by_id(id_protocolo)
    if protocolo is None:
        current_app.logger.warning("Intento de borrar protocolo inexistente %s", id_protocolo)
        raise LookupError(ERROR_PROTOCOLO_NO_EXISTE.format(id_protocolo))

    try:
        session.delete(protocolo)
        session.commit()
        current_app.logger.info("Protocolo eliminado: %s", protocolo)
        return True
    except SQLAlchemyError as e:
        session.rollback()
        current_app.logger.error("Error SQL al eliminar protocolo: %s", e)
        raise
