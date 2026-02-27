"""Servicio de equipos.

Maneja la lógica de CRUD para equipos, incluyendo:
- Recuperación de equipos con carga optimizada de relaciones
- Creación/actualización/eliminación de equipos
- Gestión de membresía (añadir/remover miembros)
- Validación de capacidad y relaciones
"""

from typing import Optional, List
from flask import current_app
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.exc import SQLAlchemyError

from app import Equipo, Usuario
from app.db import session
from app.enums.tipos import EstadoEquipo
from app.services import usuarios_services

# --- CONSTANTES ---
ERROR_EQUIPO_NOT_FOUND = "Equipo no encontrado"
ERROR_USUARIO_NOT_FOUND = "Usuario no encontrado"
ERROR_REQUIRED_FIELDS = "Nombre, estado y comandante son campos obligatorios"
ERROR_INVALID_INPUT = "Dato de entrada inválido"
ERROR_CAPACITY_EXCEEDED = "El equipo ha alcanzado su capacidad máxima de miembros"
ERROR_COMANDANTE_CANNOT_REMOVE = (
    "No se puede remover / eliminar al comandante del equipo"
)


# --- FUNCIONES DE CONSULTA (READ) ---


def get_all_equipos() -> List[Equipo]:
    """Retorna todos los equipos con relaciones precargadas.

    Optimiza consultas usando selectinload y joinedload para evitar el problema
    de N+1 queries. Carga eficientemente miembros, comandantes, jerarquías y
    resultados históricos.

    Returns:
        List[Equipo]: Lista de todos los equipos en el sistema con relaciones.

    Example:
        >>> equipos = get_all_equipos()
        >>> for equipo in equipos:
        ...     print(f"{equipo.nombre_equipo}: {len(equipo.miembros)} miembros")
    """
    try:
        equipos = (
            session.query(Equipo)
            .options(
                selectinload(Equipo.miembros).joinedload(Usuario.jerarquia),
                selectinload(Equipo.comandante).joinedload(Usuario.jerarquia),
                selectinload(Equipo.resultados),
            )
            .all()
        )
        current_app.logger.debug(f"Se obtuvieron {len(equipos)} equipos")
        return equipos
    except SQLAlchemyError as e:
        current_app.logger.exception(f"Error obteniendo todos los equipos: {e}")
        return []


def get_equipos_by_id(id_equipo: int) -> Optional[Equipo]:
    """Retorna un equipo específico por su ID con relaciones precargadas.

    Args:
        id_equipo (int): ID del equipo a recuperar.

    Returns:
        Optional[Equipo]: Objeto Equipo si existe, None en caso contrario.

    Raises:
        TypeError: Si id_equipo no es un entero válido.

    Example:
        >>> equipo = get_equipos_by_id(1)
        >>> equipo.nombre_equipo
        'Alpha Team'
    """
    if not isinstance(id_equipo, int):
        raise TypeError(f"id_equipo debe ser int, recibido {type(id_equipo)}")

    try:
        equipo = (
            session.query(Equipo)
            .options(
                selectinload(Equipo.miembros),
                joinedload(Equipo.comandante),
            )
            .filter_by(id_equipo=id_equipo)
            .first()
        )

        if equipo:
            current_app.logger.debug(
                f"Equipo {id_equipo} recuperado: {equipo.nombre_equipo}"
            )
        return equipo
    except SQLAlchemyError as e:
        current_app.logger.exception(f"Error obteniendo equipo {id_equipo}: {e}")
        return None


# --- FUNCIONES DE CREACIÓN (CREATE) ---


def create_equipo(
    nombre_equipo: str,
    estado_equipo: str,
    id_comandante: int,
    lema_equipo: Optional[str] = None,
    maximo_miembros: Optional[int] = None,
    color_equipo: Optional[str] = None,
) -> Optional[Equipo]:
    """Crea un nuevo equipo en el sistema.

    Inicializa un equipo con un comandante como primer miembro automáticamente.
    Valida que los campos requeridos se proporcionen y que los tipos sean correctos.

    Args:
        nombre_equipo (str): Nombre del equipo (requerido, no vacío).
        estado_equipo (str): Estado del equipo como string enum (ej: "ACTIVO").
        id_comandante (int): ID del usuario que será comandante del equipo.
        lema_equipo (Optional[str]): Lema o lema del equipo. Defaults to None.
        maximo_miembros (Optional[int]): Capacidad máxima de miembros. Defaults to None.
        color_equipo (Optional[str]): Color identificativo del equipo. Defaults to None.

    Returns:
        Optional[Equipo]: Equipo creado si es exitoso, None si falla.

    Raises:
        ValueError: Si los campos requeridos están vacíos o ausentes.
        TypeError: Si la conversión de tipos falla.

    Example:
        >>> equipo = create_equipo(
        ...     nombre_equipo="Alpha Team",
        ...     estado_equipo="ACTIVO",
        ...     id_comandante=5,
        ...     lema_equipo="Venceremos",
        ...     maximo_miembros=12
        ... )
        >>> equipo.id_equipo
        1
    """
    # Validar campos requeridos
    if not all([nombre_equipo, estado_equipo, id_comandante]):
        raise ValueError(ERROR_REQUIRED_FIELDS)

    if isinstance(nombre_equipo, str) and not nombre_equipo.strip():
        raise ValueError(ERROR_REQUIRED_FIELDS)

    try:
        estado_enum = EstadoEquipo[estado_equipo]
        id_comandante_int = int(id_comandante)
    except (KeyError, ValueError, TypeError) as e:
        raise TypeError(f"{ERROR_INVALID_INPUT}: {e}")

    try:
        nuevo_equipo = Equipo(
            nombre_equipo=nombre_equipo.strip(),
            lema_equipo=lema_equipo.strip() if lema_equipo else None,
            maximo_miembros=maximo_miembros,
            color_equipo=color_equipo,
            estado_equipo=estado_enum,
            id_comandante=id_comandante_int,
        )

        # Protocolo de iniciación: el comandante es el primer miembro del equipo
        comandante_user = usuarios_services.get_usuarios_by_id(id_comandante_int)
        if comandante_user:
            nuevo_equipo.agregar_miembro(comandante_user)
            current_app.logger.debug(
                f"Comandante {id_comandante_int} añadido como primer miembro del equipo"
            )
        else:
            current_app.logger.warning(
                f"No se encontró comandante con ID {id_comandante_int}"
            )

        session.add(nuevo_equipo)
        session.commit()
        current_app.logger.info(
            f"Equipo creado exitosamente: {nuevo_equipo.nombre_equipo} (ID: {nuevo_equipo.id_equipo})"
        )
        return nuevo_equipo

    except SQLAlchemyError as e:
        session.rollback()
        current_app.logger.exception(f"Error creando equipo: {e}")
        return None


# --- FUNCIONES DE ACTUALIZACIÓN (UPDATE) ---


def update_equipo(
    id_equipo: int,
    nombre_equipo: Optional[str] = None,
    lema_equipo: Optional[str] = None,
    maximo_miembros: Optional[int] = None,
    color_equipo: Optional[str] = None,
    estado_equipo: Optional[str] = None,
    id_comandante: Optional[int] = None,
) -> Optional[Equipo]:
    """Actualiza un equipo existente con los campos proporcionados.

    Solo actualiza los campos que se proporcionan (pattern: sparse update).
    Si se cambia el comandante, asegura que el nuevo comandante esté en la lista
    de miembros.

    Args:
        id_equipo (int): ID del equipo a actualizar.
        nombre_equipo (Optional[str]): Nuevo nombre si se proporciona. Defaults to None.
        lema_equipo (Optional[str]): Nuevo lema si se proporciona. Defaults to None.
        maximo_miembros (Optional[int]): Nueva capacidad si se proporciona. Defaults to None.
        color_equipo (Optional[str]): Nuevo color si se proporciona. Defaults to None.
        estado_equipo (Optional[str]): Nuevo estado si se proporciona. Defaults to None.
        id_comandante (Optional[int]): Nuevo comandante si se proporciona. Defaults to None.

    Returns:
        Optional[Equipo]: Equipo actualizado si es exitoso, None si falla.

    Raises:
        ValueError: Si el equipo no existe.
        TypeError: Si la conversión de tipos falla.

    Example:
        >>> equipo = update_equipo(1, nombre_equipo="Nueva Alfa")
        >>> equipo.nombre_equipo
        'Nueva Alfa'
    """
    if not isinstance(id_equipo, int):
        raise TypeError(f"id_equipo debe ser int, recibido {type(id_equipo)}")

    equipo_existente = get_equipos_by_id(id_equipo)
    if not equipo_existente:
        raise ValueError(ERROR_EQUIPO_NOT_FOUND)

    try:
        # Actualizar campos proporcionados
        if nombre_equipo is not None:
            equipo_existente.nombre_equipo = nombre_equipo.strip()
            current_app.logger.debug(f"Equipo {id_equipo}: nombre actualizado")

        if lema_equipo is not None:
            equipo_existente.lema_equipo = lema_equipo.strip() if lema_equipo else None
            current_app.logger.debug(f"Equipo {id_equipo}: lema actualizado")

        if maximo_miembros is not None:
            equipo_existente.maximo_miembros = int(maximo_miembros)
            current_app.logger.debug(f"Equipo {id_equipo}: capacidad actualizada")

        if color_equipo is not None:
            equipo_existente.color_equipo = color_equipo
            current_app.logger.debug(f"Equipo {id_equipo}: color actualizado")

        if estado_equipo is not None:
            equipo_existente.estado_equipo = EstadoEquipo[estado_equipo]
            current_app.logger.debug(f"Equipo {id_equipo}: estado actualizado")

        if id_comandante is not None:
            id_comandante_int = int(id_comandante)
            equipo_existente.id_comandante = id_comandante_int

            # Asegurarse de que el nuevo comandante esté en la lista de miembros
            nuevo_comandante = usuarios_services.get_usuarios_by_id(id_comandante_int)
            if nuevo_comandante:
                # Usamos el helper del modelo. Si el equipo está lleno, esto lanzará ValueError, lo cual es correcto.
                if not equipo_existente.es_miembro(nuevo_comandante.id_usuario):
                    equipo_existente.agregar_miembro(nuevo_comandante)
                    current_app.logger.debug(
                        f"Equipo {id_equipo}: nuevo comandante {id_comandante_int} añadido a miembros"
                    )
            else:
                current_app.logger.warning(
                    f"Equipo {id_equipo}: comandante {id_comandante_int} no encontrado"
                )

        session.commit()
        current_app.logger.info(f"Equipo {id_equipo} actualizado exitosamente")
        return equipo_existente

    except (KeyError, ValueError, TypeError) as e:
        session.rollback()
        current_app.logger.exception(f"Error actualizando equipo {id_equipo}: {e}")
        raise TypeError(f"{ERROR_INVALID_INPUT}: {e}")
    except SQLAlchemyError as e:
        session.rollback()
        current_app.logger.exception(
            f"Error de base de datos al actualizar equipo {id_equipo}: {e}"
        )
        return None


# --- FUNCIONES DE ELIMINACIÓN (DELETE) ---


def delete_equipo(id_equipo: int) -> bool:
    """Elimina un equipo del sistema.

    Args:
        id_equipo (int): ID del equipo a eliminar.

    Returns:
        bool: True si la eliminación fue exitosa, False en caso contrario.

    Raises:
        ValueError: Si el equipo no existe.
        TypeError: Si id_equipo no es un entero válido.

    Example:
        >>> success = delete_equipo(1)
        >>> success
        True
    """
    if not isinstance(id_equipo, int):
        raise TypeError(f"id_equipo debe ser int, recibido {type(id_equipo)}")

    equipo = get_equipos_by_id(id_equipo)
    if not equipo:
        raise ValueError(ERROR_EQUIPO_NOT_FOUND)

    try:
        session.delete(equipo)
        session.commit()
        current_app.logger.info(f"Equipo {id_equipo} eliminado exitosamente")
        return True
    except SQLAlchemyError as e:
        session.rollback()
        current_app.logger.exception(f"Error eliminando equipo {id_equipo}: {e}")
        return False


# --- FUNCIONES DE GESTIÓN DE MEMBRESÍA ---


def add_member_to_equipo(id_equipo: int, id_usuario: int) -> bool:
    """Añade un usuario como miembro de un equipo.

    Valida que:
    - El equipo y usuario existan
    - Hay capacidad disponible en el equipo
    - El usuario no ya es miembro

    Args:
        id_equipo (int): ID del equipo.
        id_usuario (int): ID del usuario a añadir.

    Returns:
        bool: True si el usuario fue añadido exitosamente, False en caso contrario.

    Raises:
        ValueError: Si el equipo/usuario no existen o si se excede capacidad.
        TypeError: Si los IDs no son enteros válidos.

    Example:
        >>> success = add_member_to_equipo(1, 5)
        >>> success
        True
    """
    if not isinstance(id_equipo, int) or not isinstance(id_usuario, int):
        raise TypeError("id_equipo e id_usuario deben ser enteros")

    equipo = get_equipos_by_id(id_equipo)
    if not equipo:
        raise ValueError(ERROR_EQUIPO_NOT_FOUND)

    usuario = session.query(Usuario).filter_by(id_usuario=id_usuario).first()
    if not usuario:
        raise ValueError(ERROR_USUARIO_NOT_FOUND)

    try:
        # Delegamos la lógica al modelo (Encapsulamiento)
        try:
            agregado = equipo.agregar_miembro(usuario)
            if not agregado:
                current_app.logger.info(
                    f"Usuario {id_usuario} ya es miembro de equipo {id_equipo}"
                )
                return True
        except ValueError:
            # Capturamos el error de capacidad del modelo y lanzamos el mensaje esperado por el controlador
            current_app.logger.warning(
                f"Intento de añadir miembro a equipo {id_equipo} con capacidad llena"
            )
            raise ValueError(f"{ERROR_CAPACITY_EXCEEDED} ({equipo.maximo_miembros})")
        session.commit()
        current_app.logger.info(
            f"Usuario {id_usuario} añadido como miembro de equipo {id_equipo}"
        )
        return True

    except SQLAlchemyError as e:
        session.rollback()
        current_app.logger.exception(
            f"Error añadiendo miembro a equipo {id_equipo}: {e}"
        )
        return False


def remove_member_from_equipo(id_equipo: int, id_usuario: int) -> bool:
    """Remueve un usuario como miembro de un equipo.

    No permite remover al comandante del equipo (protección de integridad).

    Args:
        id_equipo (int): ID del equipo.
        id_usuario (int): ID del usuario a remover.

    Returns:
        bool: True si el usuario fue removido exitosamente, False en caso contrario.

    Raises:
        ValueError: Si se intenta remover al comandante.
        TypeError: Si los IDs no son enteros válidos.

    Example:
        >>> success = remove_member_from_equipo(1, 5)
        >>> success
        True
    """
    if not isinstance(id_equipo, int) or not isinstance(id_usuario, int):
        raise TypeError("id_equipo e id_usuario deben ser enteros")

    equipo = get_equipos_by_id(id_equipo)
    if not equipo:
        raise ValueError(ERROR_EQUIPO_NOT_FOUND)

    usuario = session.query(Usuario).filter_by(id_usuario=id_usuario).first()
    if not usuario:
        return True  # Nada que remover

    try:
        # Proteger al comandante
        if equipo.es_comandante(id_usuario):
            current_app.logger.warning(
                f"Intento de remover comandante {id_usuario} del equipo {id_equipo}"
            )
            raise ValueError(ERROR_COMANDANTE_CANNOT_REMOVE)

        # Delegamos la remoción al modelo
        removido = equipo.remover_miembro(usuario)
        
        if removido:
            session.commit()
            current_app.logger.info(
                f"Usuario {id_usuario} removido del equipo {id_equipo}"
            )
            return True

        return True  # Ya no era miembro

    except SQLAlchemyError as e:
        session.rollback()
        current_app.logger.exception(
            f"Error removiendo miembro de equipo {id_equipo}: {e}"
        )
        return False
