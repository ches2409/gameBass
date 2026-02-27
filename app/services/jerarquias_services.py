"""Servicio de jerarquías - Gestión de roles y niveles de acceso.

Maneja la lógica de CRUD para jerarquías, incluyendo:
- Recuperación de jerarquías con relaciones precargadas
- Creación/actualización/eliminación de jerarquías
- Gestión de protocolos vinculados a cada jerarquía
- Validación de datos y consistencia
- Auditoría mediante logging
"""

from typing import Optional, List
from flask import current_app
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.exc import SQLAlchemyError

from app.db import session
from app.models.jerarquias_models import Jerarquia
from app.models.protocolos_models import Protocolo

# --- CONSTANTES DE ERROR ---
ERROR_JERARQUIA_NOT_FOUND = "Jerarquía no encontrada"
ERROR_NOMBRE_REQUIRED = "El nombre de la jerarquía es obligatorio"
ERROR_NOMBRE_MIN_LENGTH = "El nombre debe tener al menos 3 caracteres"
ERROR_INVALID_LEVEL = "El nivel de acceso debe estar entre 1 y 100"
ERROR_INVALID_COLOR = "El color debe ser un código hexadecimal válido (#RRGGBB)"
ERROR_REQUIRED_FIELDS = "Nombre, subtítulo, descripción, nivel y color son campos obligatorios"
ERROR_INVALID_INPUT = "Dato de entrada inválido"
ERROR_DATABASE = "Error en la base de datos"

# --- FUNCIONES DE CONSULTA (READ) ---


def get_all_jerarquias() -> List[Jerarquia]:
    """Retorna todas las jerarquías con relaciones precargadas.

    Optimiza las consultas usando selectinload para evitar el problema de N+1 queries.
    Carga eficientemente los protocolos vinculados a cada jerarquía.

    Returns:
        List[Jerarquia]: Lista de todas las jerarquías en el sistema con relaciones.

    Raises:
        SQLAlchemyError: Error al acceder a la base de datos.

    Example:
        >>> jerarquias = get_all_jerarquias()
        >>> for jerarquia in jerarquias:
        ...     print(f"{jerarquia.nombre_jerarquia}: {len(jerarquia.protocolos)} protocolos")
    """
    try:
        jerarquias = session.query(Jerarquia).options(
            selectinload(Jerarquia.protocolos)
        ).all()
        current_app.logger.debug(f"Se obtuvieron {len(jerarquias)} jerarquías")
        return jerarquias
    except SQLAlchemyError as e:
        current_app.logger.exception(f"Error obteniendo todas las jerarquías: {e}")
        return []


def get_jerarquia_by_id(id_jerarquia: int) -> Optional[Jerarquia]:
    """Obtiene una jerarquía específica por ID.

    Carga la jerarquía con sus relaciones (protocolos) precargadas para evitar
    consultas adicionales.

    Args:
        id_jerarquia: ID de la jerarquía a recuperar.

    Returns:
        Jerarquia: La jerarquía encontrada, o None si no existe.

    Raises:
        SQLAlchemyError: Error al acceder a la base de datos.

    Example:
        >>> jerarquia = get_jerarquia_by_id(1)
        >>> if jerarquia:
        ...     print(jerarquia.nombre_jerarquia)
    """
    try:
        jerarquia = session.query(Jerarquia).filter_by(
            id_jerarquia=id_jerarquia
        ).options(
            selectinload(Jerarquia.protocolos)
        ).first()
        return jerarquia
    except SQLAlchemyError as e:
        current_app.logger.exception(f"Error obteniendo jerarquía {id_jerarquia}: {e}")
        return None


def get_jerarquia_by_nombre(nombre: str) -> Optional[Jerarquia]:
    """Obtiene una jerarquía por nombre.

    Args:
        nombre: Nombre de la jerarquía.

    Returns:
        Jerarquia: La jerarquía encontrada, o None si no existe.

    Raises:
        SQLAlchemyError: Error al acceder a la base de datos.
    """
    try:
        jerarquia = session.query(Jerarquia).filter_by(
            nombre_jerarquia=nombre
        ).options(
            selectinload(Jerarquia.protocolos)
        ).first()
        return jerarquia
    except SQLAlchemyError as e:
        current_app.logger.exception(f"Error obteniendo jerarquía '{nombre}': {e}")
        return None


# --- FUNCIONES DE CREACIÓN (CREATE) ---


def create_jerarquia(
    nombre: str,
    subtitulo: str,
    descripcion: str,
    nivel: int,
    color: str,
    protocolos: Optional[List[Protocolo]] = None
) -> Jerarquia:
    """Crea una nueva jerarquía en el sistema.

    Valida todos los campos requeridos, verifica que el nombre sea único y que los
    valores estén en los rangos permitidos. Crea la jerarquía con los protocolos
    especificados y registra la operación en logs.

    Args:
        nombre: Nombre único de la jerarquía (mínimo 3 caracteres).
        subtitulo: Subtítulo descriptivo de la jerarquía.
        descripcion: Descripción detallada del propósito de la jerarquía.
        nivel: Nivel de acceso (1-100, mayor = más privilegios).
        color: Código hexadecimal del color (#RRGGBB).
        protocolos: Lista opcional de protocolos vinculados.

    Returns:
        Jerarquia: La nueva jerarquía creada con todas sus relaciones.

    Raises:
        ValueError: Si campos requeridos faltan, son inválidos o si el nombre ya existe.
        SQLAlchemyError: Error al crear en la base de datos.

    Example:
        >>> admin_jerarquia = create_jerarquia(
        ...     nombre="ADMIN",
        ...     subtitulo="Administrador",
        ...     descripcion="Acceso total al sistema",
        ...     nivel=100,
        ...     color="#FF0000"
        ... )
    """
    # 1. Validar campos requeridos
    if not all([nombre, subtitulo, descripcion, nivel is not None, color]):
        raise ValueError(ERROR_REQUIRED_FIELDS)

    # 2. Validar nombre (mínimo 3 caracteres)
    if len(nombre.strip()) < 3:
        raise ValueError(ERROR_NOMBRE_MIN_LENGTH)

    # 3. Validar nivel (1-100)
    if not isinstance(nivel, int) or not (1 <= nivel <= 100):
        raise ValueError(ERROR_INVALID_LEVEL)

    # 4. Validar color (formato hexadecimal #RRGGBB)
    if not _es_color_valido(color):
        raise ValueError(ERROR_INVALID_COLOR)

    # 5. Verificar que el nombre sea único
    if get_jerarquia_by_nombre(nombre):
        raise ValueError(f"Ya existe una jerarquía con el nombre '{nombre}'")

    try:
        # 6. Crear la jerarquía
        nueva_jerarquia = Jerarquia(
            nombre_jerarquia=nombre,
            subtitulo_jerarquia=subtitulo,
            descripcion_jerarquia=descripcion,
            nivel_acceso=nivel,
            color_hex=color,
            protocolos=protocolos if protocolos else []
        )

        # 7. Persistir en BD
        session.add(nueva_jerarquia)
        session.commit()

        current_app.logger.info(
            f"Jerarquía creada: {nueva_jerarquia.id_jerarquia} - {nombre}"
        )
        return nueva_jerarquia

    except SQLAlchemyError as e:
        session.rollback()
        current_app.logger.exception(f"Error creando jerarquía '{nombre}': {e}")
        raise


# --- FUNCIONES DE ACTUALIZACIÓN (UPDATE) ---


def update_jerarquia(
    id_jerarquia: int,
    nombre: Optional[str] = None,
    subtitulo: Optional[str] = None,
    descripcion: Optional[str] = None,
    nivel: Optional[int] = None,
    color: Optional[str] = None,
    protocolos: Optional[List[Protocolo]] = None
) -> Jerarquia:
    """Actualiza una jerarquía existente.

    Actualiza solo los campos que se proporcionen (no None). Valida los nuevos valores
    antes de persistir. Soporta actualización de protocolos vinculados.

    Args:
        id_jerarquia: ID de la jerarquía a actualizar.
        nombre: Nuevo nombre (opcional).
        subtitulo: Nuevo subtítulo (opcional).
        descripcion: Nueva descripción (opcional).
        nivel: Nuevo nivel de acceso 1-100 (opcional).
        color: Nuevo color hexadecimal (opcional).
        protocolos: Nueva lista de protocolos (opcional).

    Returns:
        Jerarquia: La jerarquía actualizada.

    Raises:
        ValueError: Si la jerarquía no existe o valores son inválidos.
        SQLAlchemyError: Error al actualizar en la base de datos.

    Example:
        >>> jerarquia = update_jerarquia(
        ...     id_jerarquia=1,
        ...     nivel=50,
        ...     color="#00FF00"
        ... )
    """
    try:
        # 1. Obtener jerarquía existente
        jerarquia = get_jerarquia_by_id(id_jerarquia)
        if not jerarquia:
            raise ValueError(ERROR_JERARQUIA_NOT_FOUND)

        # 2. Validar y actualizar campos no-None
        if nombre is not None:
            if len(nombre.strip()) < 3:
                raise ValueError(ERROR_NOMBRE_MIN_LENGTH)

            # Verificar que el nuevo nombre sea único (si es diferente)
            if nombre != jerarquia.nombre_jerarquia:
                if get_jerarquia_by_nombre(nombre):
                    raise ValueError(f"Ya existe una jerarquía con el nombre '{nombre}'")

            jerarquia.nombre_jerarquia = nombre

        if subtitulo is not None:
            jerarquia.subtitulo_jerarquia = subtitulo

        if descripcion is not None:
            jerarquia.descripcion_jerarquia = descripcion

        if nivel is not None:
            if not isinstance(nivel, int) or not (1 <= nivel <= 100):
                raise ValueError(ERROR_INVALID_LEVEL)
            jerarquia.nivel_acceso = nivel

        if color is not None:
            if not _es_color_valido(color):
                raise ValueError(ERROR_INVALID_COLOR)
            jerarquia.color_hex = color

        if protocolos is not None:
            jerarquia.protocolos = protocolos

        # 3. Persistir cambios
        session.commit()

        current_app.logger.info(
            f"Jerarquía actualizada: {id_jerarquia} - {jerarquia.nombre_jerarquia}"
        )
        return jerarquia

    except SQLAlchemyError as e:
        session.rollback()
        current_app.logger.exception(f"Error actualizando jerarquía {id_jerarquia}: {e}")
        raise


# --- FUNCIONES DE ELIMINACIÓN (DELETE) ---


def delete_jerarquia(id_jerarquia: int) -> bool:
    """Elimina una jerarquía del sistema.

    Obtiene la jerarquía por ID y la elimina si existe. Registra la operación
    en logs para auditoría.

    Args:
        id_jerarquia: ID de la jerarquía a eliminar.

    Returns:
        bool: True si se eliminó exitosamente.

    Raises:
        ValueError: Si la jerarquía no existe.
        SQLAlchemyError: Error al eliminar de la base de datos.

    Example:
        >>> success = delete_jerarquia(5)
        >>> if success:
        ...     print("Jerarquía eliminada")
    """
    try:
        # 1. Obtener jerarquía
        jerarquia = get_jerarquia_by_id(id_jerarquia)
        if not jerarquia:
            raise ValueError(ERROR_JERARQUIA_NOT_FOUND)

        # 2. Registrar nombre antes de eliminar
        nombre_jerarquia = jerarquia.nombre_jerarquia

        # 3. Eliminar
        session.delete(jerarquia)
        session.commit()

        current_app.logger.info(
            f"Jerarquía eliminada: {id_jerarquia} - {nombre_jerarquia}"
        )
        return True

    except SQLAlchemyError as e:
        session.rollback()
        current_app.logger.exception(f"Error eliminando jerarquía {id_jerarquia}: {e}")
        raise


# --- FUNCIONES DE NEGOCIO (BUSINESS LOGIC) ---


def vincular_protocolo(id_jerarquia: int, id_protocolo: int) -> Jerarquia:
    """Vincula un protocolo a una jerarquía (relación M:N).

    Args:
        id_jerarquia: ID de la jerarquía.
        id_protocolo: ID del protocolo.

    Returns:
        Jerarquia: La jerarquía actualizada.

    Raises:
        ValueError: Si jerarquía o protocolo no existen.
        SQLAlchemyError: Error de base de datos.

    Example:
        >>> jerarquia = vincular_protocolo(id_jerarquia=1, id_protocolo=5)
    """
    try:
        jerarquia = get_jerarquia_by_id(id_jerarquia)
        if not jerarquia:
            raise ValueError(ERROR_JERARQUIA_NOT_FOUND)

        protocolo = session.query(Protocolo).filter_by(
            id_protocolo=id_protocolo
        ).first()
        if not protocolo:
            raise ValueError("Protocolo no encontrado")

        # Evitar duplicados
        if protocolo not in jerarquia.protocolos:
            jerarquia.protocolos.append(protocolo)
            session.commit()
            current_app.logger.info(
                f"Protocolo {id_protocolo} vinculado a jerarquía {id_jerarquia}"
            )

        return jerarquia

    except SQLAlchemyError as e:
        session.rollback()
        current_app.logger.exception(
            f"Error vinculando protocolo {id_protocolo} a jerarquía {id_jerarquia}: {e}"
        )
        raise


def desvincular_protocolo(id_jerarquia: int, id_protocolo: int) -> Jerarquia:
    """Desvincula un protocolo de una jerarquía.

    Args:
        id_jerarquia: ID de la jerarquía.
        id_protocolo: ID del protocolo.

    Returns:
        Jerarquia: La jerarquía actualizada.

    Raises:
        ValueError: Si jerarquía o protocolo no existen.
        SQLAlchemyError: Error de base de datos.
    """
    try:
        jerarquia = get_jerarquia_by_id(id_jerarquia)
        if not jerarquia:
            raise ValueError(ERROR_JERARQUIA_NOT_FOUND)

        protocolo = session.query(Protocolo).filter_by(
            id_protocolo=id_protocolo
        ).first()
        if not protocolo:
            raise ValueError("Protocolo no encontrado")

        if protocolo in jerarquia.protocolos:
            jerarquia.protocolos.remove(protocolo)
            session.commit()
            current_app.logger.info(
                f"Protocolo {id_protocolo} desvinculado de jerarquía {id_jerarquia}"
            )

        return jerarquia

    except SQLAlchemyError as e:
        session.rollback()
        current_app.logger.exception(
            f"Error desvinculando protocolo {id_protocolo} de jerarquía {id_jerarquia}: {e}"
        )
        raise


# --- FUNCIONES AUXILIARES (HELPERS) ---


def _es_color_valido(color: str) -> bool:
    """Valida que el color sea un código hexadecimal válido (#RRGGBB).

    Args:
        color: Cadena de color a validar.

    Returns:
        bool: True si es un color hexadecimal válido, False en caso contrario.

    Example:
        >>> _es_color_valido("#FF0000")
        True
        >>> _es_color_valido("rojo")
        False
    """
    if not isinstance(color, str):
        return False

    if not color.startswith('#'):
        return False

    if len(color) != 7:
        return False

    try:
        int(color[1:], 16)
        return True
    except ValueError:
        return False
