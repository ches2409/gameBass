"""Servicio de resultados - Gestión de podios y rankings finales.

Encapsula la lógica para trabajar con `Resultado`, una entidad histórica que
resume la performance de un usuario o equipo en un torneo.

Responsabilidades principales:
- Consultas de resultados (todos, por torneo, por usuario, por ID)
- Creación de resultados (inmutables)
- Validaciones de integridad (posiciones >=1, puntajes >=0)
- Eliminación en caso de error administrativo
- Carga optimizada de relaciones para reportes
- Manejo transaccional y logging exhaustivo

Nota de diseño: los `Resultado` son conceptualmente inmutables. No existe
`update_resultado`; si se debe corregir uno se elimina y crea uno nuevo.
"""

from typing import Optional, List
from flask import current_app
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError

from app.db import session
from app import Resultado, Torneo, Usuario, Equipo


# --- CONSTANTES DE ERROR ---
ERROR_RESULTADO_NOT_FOUND = "Resultado no encontrado"
ERROR_REQUIRED_FIELDS = (
    "Torneo, usuario, posición final y puntaje_total son obligatorios"
)
ERROR_INVALID_POSITION = "La posición final debe ser un entero >= 1"
ERROR_INVALID_SCORE = "El puntaje total debe ser un entero >= 0"
ERROR_INVALID_INPUT = "Dato de entrada inválido"
ERROR_DATABASE = "Error en la base de datos"


# --- CONSULTAS (READ) ---

def get_all_resultados() -> List[Resultado]:
    """Retorna todos los resultados con relaciones precargadas.

    Carga torneo, usuario y equipo para evitar consultas N+1 en la vista de
    ranking.
    """
    try:
        current_app.logger.debug("Obteniendo todos los resultados")
        resultados = (
            session.query(Resultado)
            .options(
                selectinload(Resultado.torneo),
                selectinload(Resultado.usuario),
                selectinload(Resultado.equipo),
            )
            .all()
        )
        current_app.logger.debug(f"Encontrados {len(resultados)} resultados")
        return resultados
    except SQLAlchemyError as e:
        current_app.logger.exception(f"Error al obtener resultados: {e}")
        raise


def get_resultado_by_id(id_resultado: int) -> Optional[Resultado]:
    """Busca un resultado por su ID primario."""
    try:
        current_app.logger.debug(f"Buscando resultado ID={id_resultado}")
        return (
            session.query(Resultado)
            .options(
                selectinload(Resultado.torneo),
                selectinload(Resultado.usuario),
                selectinload(Resultado.equipo),
            )
            .filter_by(id_resultado=id_resultado)
            .first()
        )
    except SQLAlchemyError as e:
        current_app.logger.exception(f"Error buscando resultado {id_resultado}: {e}")
        raise


def get_resultados_by_torneo(id_torneo: int) -> List[Resultado]:
    """Todos los resultados de un torneo específico."""
    try:
        resultados = (
            session.query(Resultado)
            .options(selectinload(Resultado.usuario), selectinload(Resultado.equipo))
            .filter_by(id_torneo=id_torneo)
            .order_by(Resultado.posicion_final)
            .all()
        )
        return resultados
    except SQLAlchemyError as e:
        current_app.logger.exception(f"Error resultados por torneo {id_torneo}: {e}")
        raise


def get_resultados_by_usuario(id_usuario: int) -> List[Resultado]:
    """Todos los resultados asociados a un usuario."""
    try:
        resultados = (
            session.query(Resultado)
            .options(selectinload(Resultado.torneo), selectinload(Resultado.equipo))
            .filter_by(id_usuario=id_usuario)
            .all()
        )
        return resultados
    except SQLAlchemyError as e:
        current_app.logger.exception(f"Error resultados por usuario {id_usuario}: {e}")
        raise


# --- CREACIÓN / ELIMINACIÓN (NO ACTUALIZACIÓN) ---

def create_resultado(
    id_torneo: int,
    id_usuario: int,
    posicion_final: int,
    puntaje_total: int,
    victoria_confirmada: bool = False,
    recompensa_entregada: Optional[str] = None,
    id_equipo: Optional[int] = None,
) -> Resultado:
    """Inserta un nuevo resultado después de validar todas las reglas.

    Args:
        id_torneo: torneo asociado.
        id_usuario: ganador individual.
        posicion_final: lugar en el podio (>=1).
        puntaje_total: puntaje acumulado (>=0).
        victoria_confirmada: flag de auditoría.
        recompensa_entregada: descripción del premio.
        id_equipo: equipo ganador, si aplica.

    Returns:
        Resultado: fila recién creada.

    Raises:
        ValueError: si falla alguna validación.
        SQLAlchemyError: error de base de datos.
    """
    try:
        # campos obligatorios
        if any(v is None for v in [id_torneo, id_usuario, posicion_final, puntaje_total]):
            raise ValueError(ERROR_REQUIRED_FIELDS)

        if not isinstance(posicion_final, int) or posicion_final < 1:
            raise ValueError(ERROR_INVALID_POSITION)
        if not isinstance(puntaje_total, int) or puntaje_total < 0:
            raise ValueError(ERROR_INVALID_SCORE)

        try:
            id_torneo = int(id_torneo)
            id_usuario = int(id_usuario)
            if id_equipo is not None:
                id_equipo = int(id_equipo)
        except (TypeError, ValueError) as e:
            raise ValueError(f"{ERROR_INVALID_INPUT}: {e}")

        # verificar existencia
        if not session.get(Torneo, id_torneo):
            raise ValueError("Torneo no encontrado")
        if not session.get(Usuario, id_usuario):
            raise ValueError("Usuario no encontrado")
        if id_equipo is not None and not session.get(Equipo, id_equipo):
            raise ValueError("Equipo no encontrado")

        current_app.logger.info(
            f"Creando resultado torneo={id_torneo} usuario={id_usuario} posicion={posicion_final}"
        )

        nuevo = Resultado(
            id_torneo=id_torneo,
            id_usuario=id_usuario,
            posicion_final=posicion_final,
            puntaje_total=puntaje_total,
            victoria_confirmada=victoria_confirmada,
            recompensa_entregada=recompensa_entregada,
            id_equipo=id_equipo,
        )

        session.add(nuevo)
        session.commit()
        return nuevo
    except ValueError:
        raise
    except SQLAlchemyError as e:
        session.rollback()
        current_app.logger.exception(f"Error creando resultado: {e}")
        raise


def delete_resultado(id_resultado: int) -> bool:
    """Elimina un resultado por ID (casos excepcionales).

    Esta operación debe usarse sólo cuando se detectó un error lógico en el
    registro original; en condiciones normales los resultados son inmutables.
    """
    try:
        res = get_resultado_by_id(id_resultado)
        if not res:
            raise ValueError(ERROR_RESULTADO_NOT_FOUND)
        current_app.logger.info(f"Eliminando resultado ID={id_resultado}")
        session.delete(res)
        session.commit()
        return True
    except ValueError:
        raise
    except SQLAlchemyError as e:
        session.rollback()
        current_app.logger.exception(f"Error eliminando resultado {id_resultado}: {e}")
        raise
