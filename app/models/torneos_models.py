"""Modelo de Torneo - Campeonatos y competencias de GameBass.

Define torneos que se ejecutan dentro de un juego específico. Cada torneo
incluye información de fechas, estado, capacidad y premios. Actúa como
contenedor central para registros (participaciones) y resultados (podios).

Características:
- Nombre único dentro de su juego
- Rango de acceso (nivel mínimo requerido para participar)
- Control de capacidad (máximo de competidores)
- Fechas de creación, inicio y finalización
- Estado del torneo (draft, activo, finalizado, cancelado, etc.)
- Premios/recompensas para ganadores
- Relaciones: 1 Juego, N Registros, N Resultados

Ejemplo de uso:
    >>> torneo = Torneo(
    ...     nombre_torneo="VCT 2026 Brazil",
    ...     recompensa_torneo="$100,000 USD",
    ...     nivel_acceso_min=60,
    ...     max_competidores=16,
    ...     id_juego=3
    ... )
    >>> session.add(torneo)
    >>> session.commit()
    >>> torneo.registros_count
    8
"""

from sqlalchemy import Integer, String, DateTime, func, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, List, Optional

from app.db import Base
from app.enums.tipos import EstadoTorneo
from sqlalchemy import Enum as _Enum

if TYPE_CHECKING:
    from .juegos_models import Juego
    from .registros_models import Registro
    from .resultados_models import Resultado


class Torneo(Base):
    """Representa un campeonato o competencia en GameBass.
    
    Un Torneo encapsula:
        - Identidad: nombre del campeonato (VCT International, etc.)
        - Scope: juego específico (1:N con Juego)
        - Restricciones: nivel mínimo de acceso requerido
        - Capacidad: número máximo de participantes / equipos
        - Temporalidad: fechas de creación, inicio, finalización
        - Recompensas: premios para ganadores
        - Participación: lista de registros (quién participa)
        - Resultados: cuadro de honor y podios
    
    Los torneos son la unidad de competencia principal en la plataforma,
    permitiendo segmentar eventos por juego, nivel y período temporal.
    """

    __tablename__ = "torneos"

    __table_args__ = (
        CheckConstraint(
            'length(nombre_torneo) >= 3',
            name='check_nombre_torneo_minlen'
        ),
        CheckConstraint(
            'length(recompensa_torneo) >= 1',
            name='check_recompensa_torneo_minlen'
        ),
        CheckConstraint(
            'nivel_acceso_min >= 0 AND nivel_acceso_min <= 100',
            name='check_nivel_acceso_min_range'
        ),
        CheckConstraint(
            'max_competidores >= 2 AND max_competidores <= 1000',
            name='check_max_competidores_range'
        ),
        CheckConstraint(
            'fecha_inicio IS NULL OR fecha_fin IS NULL OR fecha_inicio < fecha_fin',
            name='check_fechas_coherente'
        ),
        {
            "sqlite_autoincrement": True,
            "comment": "Campeonatos y competencias organizadas por juego"
        },
    )

    id_torneo: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    nombre_torneo: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Nombre del torneo (ej: VCT International, Worlds 2026)"
    )

    recompensa_torneo: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Premio/recompensa asignada (ej: $100,000 USD, skin exclusivo)"
    )

    nivel_acceso_min: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        index=True,
        comment="Nivel mínimo requerido (0-100) para participar"
    )

    estado_torneo: Mapped[EstadoTorneo] = mapped_column(
        _Enum(
            EstadoTorneo,
            name="estado_torneo_enum",
            nullable=False,
            default=EstadoTorneo.draft,
            server_default=EstadoTorneo.draft.name
        ),
        index=True,
        comment="Estado actual (draft, programado, activo, finalizado, cancelado)"
    )

    max_competidores: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=16,
        comment="Capacidad máxima de participantes (2-1000)"
    )

    fecha_creacion: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="Fecha de creación del torneo"
    )

    fecha_inicio: Mapped[Optional[DateTime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha programada de inicio (nullable si aún no confirmada)"
    )

    fecha_fin: Mapped[Optional[DateTime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha de fin planificada (debe ser > fecha_inicio si ambas existen)"
    )

    # --- Clave Foránea (Foreign Key) ---
    id_juego: Mapped[int] = mapped_column(
        ForeignKey("juegos.id_juego", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Juego en el que se ejecuta este torneo"
    )

    # --- RELACIONES ---
    # 1:N - Un torneo tiene muchos registros (participaciones)
    registros: Mapped[List["Registro"]] = relationship(
        "Registro",
        back_populates="torneo",
        cascade="all, delete-orphan"
    )

    # 1:N - Un torneo tiene muchos resultados (podios)
    resultados: Mapped[List["Resultado"]] = relationship(
        "Resultado",
        back_populates="torneo"
    )

    # N:1 - Inversa, permite acceder al juego desde torneo
    juego: Mapped["Juego"] = relationship(
        "Juego",
        back_populates="torneos"
    )

    def __repr__(self) -> str:
        """Representación técnica para debugging."""
        registros_cnt = len(self.registros) if self.registros else 0
        resultados_cnt = len(self.resultados) if self.resultados else 0
        return (
            f"<Torneo(id={self.id_torneo}, "
            f"nombre='{self.nombre_torneo}', "
            f"estado='{self.estado_torneo.name}', "
            f"juego={self.id_juego}, "
            f"registros={registros_cnt}, "
            f"resultados={resultados_cnt})>"
        )

    def __str__(self) -> str:
        """Representación amigable para UI."""
        return self.nombre_torneo

    # ---------- Propiedades calculadas ----------

    @property
    def registros_count(self) -> int:
        """Cantidad actual de participantes registrados."""
        return len(self.registros) if self.registros else 0

    @property
    def resultados_count(self) -> int:
        """Cantidad de podios/resultados registrados."""
        return len(self.resultados) if self.resultados else 0

    @property
    def capacidad_disponible(self) -> int:
        """Lugares restantes en el torneo."""
        return max(0, self.max_competidores - self.registros_count)

    @property
    def esta_lleno(self) -> bool:
        """¿El torneo alcanzó su capacidad máxima?"""
        return self.registros_count >= self.max_competidores

    @property
    def estado_nombre(self) -> str:
        """Nombre legible del estado actual."""
        return self.estado_torneo.name if self.estado_torneo else "desconocido"

    # ---------- Métodos helper ----------

    def puede_participar(self, nivel_acceso_usuario: int) -> bool:
        """Verifica si un usuario puede participar según su nivel.

        Args:
            nivel_acceso_usuario (int): Nivel de acceso del usuario (0-100).

        Returns:
            bool: True si el usuario cumple con el nivel mínimo requerido.

        Raises:
            TypeError: Si nivel_acceso_usuario no es int.
        """
        if not isinstance(nivel_acceso_usuario, int):
            raise TypeError(
                f"nivel_acceso_usuario debe ser int, recibido {type(nivel_acceso_usuario)}"
            )
        return nivel_acceso_usuario >= self.nivel_acceso_min

    def aceptar_registro(self) -> bool:
        """¿El torneo acepta nuevos registros sin exceder capacidad?

        Returns:
            bool: True si no está lleno.
        """
        return not self.esta_lleno

    def obtener_informacion_basica(self) -> dict:
        """Retorna información esencial del torneo para UI/API.

        Returns:
            dict: Diccionario con datos principales y estadísticas.
        """
        return {
            'id': self.id_torneo,
            'nombre': self.nombre_torneo,
            'juego_id': self.id_juego,
            'estado': self.estado_nombre,
            'nivel_minimo': self.nivel_acceso_min,
            'capacidad_maxima': self.max_competidores,
            'registrados': self.registros_count,
            'lugares_libres': self.capacidad_disponible,
            'recompensa': self.recompensa_torneo,
            'fecha_inicio': self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            'fecha_fin': self.fecha_fin.isoformat() if self.fecha_fin else None
        }

