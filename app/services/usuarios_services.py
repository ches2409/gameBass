"""Servicio de usuarios - Gestión de cuentas y autenticación.

Contiene la lógica de CRUD para usuarios, así como utilidades de
acceso (hash de contraseña, autentificación básica) y consultas paginadas.

Principales responsabilidades:
- Recuperación eficiente de usuarios con sus jerarquías
- Creación / actualización / eliminación de usuarios
- Paginación y filtros combinados
- Hashing de contraseñas y validaciones de seguridad
- Manejo de errores con logging y rollback automático
"""

from typing import Optional, Tuple, List
from flask import current_app
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError

from app import Usuario
from app.db import session
from werkzeug.security import generate_password_hash, check_password_hash

# --- CONSTANTES DE ERROR ---
ERROR_USER_NOT_FOUND = "Usuario no encontrado"
ERROR_REQUIRED_FIELDS = "Alias, email, contraseña y jerarquía son campos obligatorios"
ERROR_INVALID_EMAIL = "Email inválido"
ERROR_INVALID_INPUT = "Dato de entrada inválido"
ERROR_DATABASE = "Error en la base de datos"


def get_all_usuarios() -> List[Usuario]:
    """Retorna todos los usuarios con su jerarquía precargada.

    Se utiliza `joinedload` para evitar consultas N+1 cuando se accede a la
    jerarquía desde cada usuario.

    Returns:
        List[Usuario]: lista de objetos Usuario.

    Raises:
        SQLAlchemyError: en caso de error de base de datos.
    """
    try:
        usuarios = session.query(Usuario).options(
            joinedload(Usuario.jerarquia)
        ).all()
        current_app.logger.debug(f"Obtenidos {len(usuarios)} usuarios")
        return usuarios
    except SQLAlchemyError as e:
        current_app.logger.exception(f"Error obteniendo usuarios: {e}")
        return []


def get_available_users_paginated(
    excluded_ids: Optional[List[int]],
    page: int,
    per_page: int
) -> Tuple[List[Usuario], int]:
    """Obtiene usuarios paginados excluyendo ciertos IDs.

    Args:
        excluded_ids: lista de IDs de usuarios a excluir (por ejemplo, ya en equipo).
        page: número de página (1-based).
        per_page: cantidad de elementos por página.

    Returns:
        tuple: (lista de usuarios, total de registros antes de paginar).

    Raises:
        SQLAlchemyError: si ocurre un error en la consulta.
    """
    try:
        query = session.query(Usuario).options(joinedload(Usuario.jerarquia))

        if excluded_ids:
            query = query.filter(Usuario.id_usuario.notin_(excluded_ids))

        total = query.count()
        items = query.offset((page - 1) * per_page).limit(per_page).all()

        return items, total
    except SQLAlchemyError as e:
        current_app.logger.exception(f"Error en paginación de usuarios: {e}")
        return [], 0


def get_usuarios_by_id(id_usuario: int) -> Optional[Usuario]:
    """Retorna usuario por ID.

    Args:
        id_usuario: ID del usuario.

    Returns:
        Usuario o None.

    Raises:
        SQLAlchemyError: en caso de fallo en la base de datos.
    """
    try:
        return session.query(Usuario).filter_by(id_usuario=id_usuario).first()
    except SQLAlchemyError as e:
        current_app.logger.exception(f"Error obteniendo usuario {id_usuario}: {e}")
        return None


def get_usuario_by_email(email: str) -> Optional[Usuario]:
    """Busca usuario por correo electrónico.

    Args:
        email: Email a buscar.

    Returns:
        Usuario o None.
    """
    try:
        return (
            session.query(Usuario)
            .options(joinedload(Usuario.jerarquia))
            .filter_by(email_usuario=email)
            .first()
        )
    except SQLAlchemyError as e:
        current_app.logger.exception(f"Error buscando usuario por email '{email}': {e}")
        return None


def create_usuario(
    alias_usuario: str,
    email_usuario: str,
    password: str,
    foto_usuario: Optional[str],
    id_jerarquia: int
) -> Usuario:
    """Crea un nuevo usuario con contraseña hasheada.

    Args:
        alias_usuario: nombre visible del usuario.
        email_usuario: correo electrónico único.
        password: contraseña en texto plano (será hasheada).
        foto_usuario: URL o path de la foto (opcional).
        id_jerarquia: ID de la jerarquía asignada.

    Returns:
        Usuario: instancia creada.

    Raises:
        ValueError: campos obligatorios faltantes o email inválido.
        TypeError: conversión de datos inválida.
        SQLAlchemyError: error al persistir en la base de datos.
    """
    # validaciones básicas
    if not alias_usuario or not email_usuario or not password or not id_jerarquia:
        raise ValueError("Alias, email, contraseña y jerarquía son obligatorios")

    if "@" not in email_usuario:
        raise ValueError("Email inválido")

    try:
        id_jerarquia_int = int(id_jerarquia)
        hashed_password = generate_password_hash(password)
    except ValueError as e:
        raise TypeError(f"Dato de entrada inválido: {e}")

    try:
        nuevo_usuario = Usuario(
            alias_usuario=alias_usuario,
            email_usuario=email_usuario,
            password_usuario=hashed_password,
            foto_usuario=foto_usuario,
            id_jerarquia=id_jerarquia_int,
        )
        session.add(nuevo_usuario)
        session.commit()
        current_app.logger.info(f"Usuario creado: {nuevo_usuario.id_usuario} - {alias_usuario}")
        return nuevo_usuario
    except SQLAlchemyError as e:
        session.rollback()
        current_app.logger.exception(f"Error creando usuario {email_usuario}: {e}")
        raise


def update_usuario(
    id_usuario: int,
    alias_usuario: Optional[str] = None,
    email_usuario: Optional[str] = None,
    password: Optional[str] = None,
    foto_usuario: Optional[str] = None,
    id_jerarquia: Optional[int] = None
) -> Usuario:
    """Actualiza campos de un usuario existente.

    Solo los valores que no sean None serán modificados.

    Args:
        id_usuario: ID del usuario a actualizar.
        alias_usuario: nuevo alias (opcional).
        email_usuario: nuevo email (opcional).
        password: nueva contraseña (será hasheada) (opcional).
        foto_usuario: nueva foto (opcional).
        id_jerarquia: nueva jerarquía (opcional).

    Returns:
        Usuario: instancia actualizada.

    Raises:
        ValueError: usuario no existe o datos inválidos.
        TypeError: conversión de datos inválida.
        SQLAlchemyError: error en la base de datos.
    """
    usuario = get_usuarios_by_id(id_usuario)

    if not usuario:
        raise ValueError("Usuario no encontrado")

    try:
        if alias_usuario is not None:
            usuario.alias_usuario = alias_usuario
        if email_usuario is not None:
            if "@" not in email_usuario:
                raise ValueError("Email inválido")
            usuario.email_usuario = email_usuario
        if password:
            usuario.password_usuario = generate_password_hash(password)
        if foto_usuario is not None:
            usuario.foto_usuario = foto_usuario
        if id_jerarquia is not None:
            usuario.id_jerarquia = int(id_jerarquia)
    except (KeyError, ValueError) as e:
        session.rollback()
        current_app.logger.exception(f"Error validando actualización de usuario {id_usuario}: {e}")
        raise TypeError(f"Dato de entrada inválido al actualizar: {e}")

    try:
        session.commit()
        current_app.logger.info(f"Usuario actualizado: {id_usuario}")
        return usuario
    except SQLAlchemyError as e:
        session.rollback()
        current_app.logger.exception(f"Error actualizando usuario {id_usuario}: {e}")
        raise


def delete_usuario(id_usuario: int) -> bool:
    """Elimina un usuario por ID.

    Args:
        id_usuario: ID del usuario a eliminar.

    Returns:
        bool: True si se eliminó correctamente.

    Raises:
        ValueError: si el usuario no existe.
        SQLAlchemyError: en caso de fallo de BD.
    """
    usuario = get_usuarios_by_id(id_usuario)

    if not usuario:
        raise ValueError("Usuario no encontrado")

    try:
        session.delete(usuario)
        session.commit()
        current_app.logger.info(f"Usuario eliminado: {id_usuario}")
        return True
    except SQLAlchemyError as e:
        session.rollback()
        current_app.logger.exception(f"Error eliminando usuario {id_usuario}: {e}")
        raise


# --- FUNCIONES DE NEGOCIO / AUTENTICACIÓN ---

def authenticate_user(email: str, password: str) -> Optional[Usuario]:
    """Verifica credenciales básicas (email + contraseña).

    Args:
        email: correo del usuario.
        password: contraseña en texto plano.

    Returns:
        Usuario si la autenticación es exitosa, None de lo contrario.
    """
    user = get_usuario_by_email(email)
    if not user:
        return None
    if check_password_hash(user.password_usuario, password):
        current_app.logger.debug(f"Autenticación exitosa para {email}")
        return user
    current_app.logger.warning(f"Fallo de autenticación para {email}")
    return None
