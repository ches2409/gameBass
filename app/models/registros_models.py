"""Modelo de Registro - Telemetría de participaciones en torneos.

Define la participación de un usuario (individual o en equipo) en un torneo
específico jugando un rol particular. Cada registro captura:

- Usuario que participó
- Torneo en el que participó
- Juego que se jugó
- Rol que adoptó el usuario
- Equipo del que era miembro (si aplica)
- Puntaje o rendimiento
- Timestamp de fecha

Características:
- Relación N:N compleja entre usuarios, torneos y equipos
- Soporte para competencia individual (id_equipo NULL) y por equipos
- Scoring y telemetría de desempeño
- Auditoría temporal con fecha_registro automática

Ejemplo de uso:
    >>> registro = Registro(
    ...     id_usuario=1, id_torneo=5, id_juego=3,
    ...     id_rol=2, id_equipo=None, puntaje=1250
    ... )
    >>> session.add(registro)
    >>> session.commit()
"""

from sqlalchemy import Integer, String, DateTime, func, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, Optional

from app.db import Base

if TYPE_CHECKING:
    from .torneos_models import Torneo
    from .juegos_models import Juego
    from .usuarios_models import Usuario
    from .equipos_models import Equipo
    from .roles_models import Rol


class Registro(Base):
    """Registro de participación de usuario en un torneo.
    
    Un Registro encapsula:
        - Identidad de participante: usuario, equipo (opcional)
        - Contexto: torneo, juego en el que se jugó
        - Rol adoptado: especialidad que utilizó
        - Desempeño: puntaje obtenido
        - Auditoría: fecha exacta de participación
    
    Los registros actúan como "hechos históricos" que nunca cambian,
    permitiendo auditoría completa y análisis de métricas.
    
    Soportan dos modos:
    - Individual: id_equipo = NULL (usuario solo)
    - Equipo: id_equipo = X (usuario forma parte de equipo)
    """

    __tablename__ = "registros"

    __table_args__ = (
        CheckConstraint(
            'puntaje >= 0 AND puntaje <= 10000',
            name='check_puntaje_range'
        ),
        CheckConstraint(
            '(id_equipo IS NOT NULL) OR (id_equipo IS NULL)',
            name='check_equipo_opcional'
        ),
        {
            "sqlite_autoincrement": True,
            "comment": "Telemetría de participaciones: usuario + torneo + juego + rol + equipo"
        },
    )

    id_registro: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    puntaje: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Puntuación obtenida (0-10000, específico del juego)"
    )

    fecha_registro: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="Timestamp automático de participación"
    )

    # --- ForeignKeys (todos requeridos excepto id_equipo) ---

    id_torneo: Mapped[int] = mapped_column(
        ForeignKey("torneos.id_torneo", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Torneo en el que participó"
    )

    id_juego: Mapped[int] = mapped_column(
        ForeignKey("juegos.id_juego", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Juego que se jugó"
    )

    id_usuario: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id_usuario", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Usuario participante"
    )

    id_rol: Mapped[int] = mapped_column(
        ForeignKey("roles.id_rol", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Rol que adoptó en la partida"
    )

    id_equipo: Mapped[Optional[int]] = mapped_column(
        ForeignKey("equipos.id_equipo", ondelete="RESTRICT"),
        nullable=True,
        index=True,
        comment="Equipo (opcional si es competencia individual)"
    )

    # --- RELACIONES ---

    torneo: Mapped["Torneo"] = relationship(
        "Torneo",
        back_populates="registros"
    )

    juego: Mapped["Juego"] = relationship(
        "Juego",
        back_populates="registros"
    )

    usuario: Mapped["Usuario"] = relationship(
        "Usuario",
        back_populates="registros"
    )

    equipo: Mapped[Optional["Equipo"]] = relationship(
        "Equipo",
        back_populates="registros"
    )

    rol: Mapped["Rol"] = relationship(
        "Rol",
        back_populates="registros"
    )

    def __repr__(self) -> str:
        """Representación técnica para debugging."""
        equipo_str = f", equipo={self.id_equipo}" if self.id_equipo else ""
        return (
            f"<Registro(id={self.id_registro}, "
            f"usuario={self.id_usuario}, "
            f"torneo={self.id_torneo}, "
            f"juego={self.id_juego}, "
            f"rol={self.id_rol}, "
            f"puntaje={self.puntaje}{equipo_str})>"
        )

    def __str__(self) -> str:
        """Representación amigable para UI."""
        equipo_info = f" ({self.equipo.nombre_equipo})" if self.equipo else " (individual)"
        return f"{self.usuario.alias_usuario}{equipo_info}"

    # ---------- Propiedades calculadas ----------

    @property
    def es_individual(self) -> bool:
        """¿Esta participación fue individual (sin equipo)?"""
        return self.id_equipo is None

    @property
    def es_en_equipo(self) -> bool:
        """¿Esta participación fue en equipo?"""
        return self.id_equipo is not None

    # ---------- Métodos helper ----------

    def obtener_informacion_basica(self) -> dict:
        """Retorna información del registro para UI/reportes.

        Returns:
            dict: Información de participación con entidades relacionadas.
        """
        return {
            'id': self.id_registro,
            'usuario': self.usuario.alias_usuario if self.usuario else "Desconocido",
            'torneo': self.torneo.nombre_torneo if self.torneo else "Desconocido",
            'juego': self.juego.nombre_juego if self.juego else "Desconocido",
            'rol': self.rol.nombre_rol if self.rol else "Desconocido",
            'equipo': self.equipo.nombre_equipo if self.equipo else "Individual",
            'puntaje': self.puntaje,
            'fecha': self.fecha_registro.isoformat() if self.fecha_registro else None,
            'modo': 'Equipo' if self.es_en_equipo else 'Individual'
        }

    def obtener_puntaje_normalizado(self, max_puntaje: int = 10000) -> float:
        """Retorna puntaje como porcentaje (0-100).

        Args:
            max_puntaje (int): Puntaje máximo posible (default 10000).

        Returns:
            float: Porcentaje normalizado (0.0-100.0).

        Raises:
            ValueError: Si max_puntaje <= 0.
        """
        if max_puntaje <= 0:
            raise ValueError("max_puntaje debe ser mayor que 0")
        porcentaje = (self.puntaje / max_puntaje) * 100
        return min(100.0, max(0.0, porcentaje))

