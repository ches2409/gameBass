"""Modelo de Juego - Catálogo de títulos disponibles para competencias.

Define los juegos electrónicos que se pueden jugar en las arenas de GameBass.
Cada juego actúa como contenedor de torneos y registro de participaciones.

Características:
- Información base: nombre, motor, género
- Estado del juego (estable, beta, deprecado, etc.)
- Identidad visual: color de interfaz (#RRGGBB)
- Relaciones: múltiples torneos y registros de participación

Ejemplo de uso:
    >>> juego = Juego(
    ...     nombre_juego="Valorant",
    ...     motor_juego="Unreal Engine",
    ...     genero_juego="Tactical Shooter",
    ...     color_juego="#EE3322"
    ... )
    >>> session.add(juego)
    >>> session.commit()
    >>> juego.torneos_count
    5
"""

from sqlalchemy import Integer, String, CheckConstraint, Enum as _Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING, Optional

from app.db import Base
from app.enums.tipos import EstadoJuego

if TYPE_CHECKING:
    from .torneos_models import Torneo
    from .registros_models import Registro


class Juego(Base):
    """Representa un juego disponible en el sistema.
    
    Un Juego encapsula:
        - Identidad: nombre único (Valorant, CS2, etc.)
        - Infraestructura: motor que ejecuta (Unreal, Source, etc.)
        - Categorización: género (FPS, MOBA, RPG, etc.)
        - Estado: nivel de soporte (estable, beta, deprecado)
        - Presentación: color identificador para UI
        - Contenido: lista de torneos y participaciones
    
    Los juegos actúan como contenedores de campeonatos y registros,
    permitiendo administrar múltiples títulos en una sola plataforma.
    """

    __tablename__ = 'juegos'

    __table_args__ = (
        CheckConstraint(
            'length(nombre_juego) >= 3',
            name='check_nombre_juego_minlen'
        ),
        CheckConstraint(
            'length(motor_juego) >= 2',
            name='check_motor_juego_minlen'
        ),
        CheckConstraint(
            'length(genero_juego) >= 3',
            name='check_genero_juego_minlen'
        ),
        CheckConstraint(
            'length(color_juego) = 7 AND color_juego LIKE ''#%''',
            name='check_color_juego_format'
        ),
        {
            "sqlite_autoincrement": True,
            "comment": "Catálogo de juegos disponibles para competencias"
        }
    )

    id_juego: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    nombre_juego: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
        comment="Nombre único del juego (ej: Valorant, CS2)"
    )

    motor_juego: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Motor gráfico/engine (ej: Unreal Engine, Source)"
    )

    genero_juego: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Género clasificatorio (ej: FPS, MOBA, RPG)"
    )

    estado_juego: Mapped[EstadoJuego] = mapped_column(
        _Enum(
            EstadoJuego,
            name="estado_juego_enum",
            nullable=False,
            default=EstadoJuego.estable,
            server_default=EstadoJuego.estable.name
        ),
        index=True,
        comment="Estado de soporte (estable, beta, deprecado, etc.)"
    )

    color_juego: Mapped[str] = mapped_column(
        String(7),
        nullable=False,
        default="#FFFFFF",
        comment="Color identificador en formato #RRGGBB"
    )

    # --- RELACIONES ---
    # 1:N - Un juego tiene muchos registros (participaciones)
    registros: Mapped[List["Registro"]] = relationship(
        "Registro",
        back_populates="juego"
    )

    # 1:N - Un juego puede tener múltiples torneos (cascada: borrar juego → borrar torneos)
    torneos: Mapped[List["Torneo"]] = relationship(
        "Torneo",
        back_populates="juego",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """Representación técnica para debugging."""
        torneos_cnt = len(self.torneos) if self.torneos else 0
        registros_cnt = len(self.registros) if self.registros else 0
        return (
            f"<Juego(id={self.id_juego}, "
            f"nombre='{self.nombre_juego}', "
            f"estado='{self.estado_juego.name}', "
            f"torneos={torneos_cnt}, "
            f"registros={registros_cnt})>"
        )

    def __str__(self) -> str:
        """Representación amigable para UI."""
        return self.nombre_juego

    # ---------- Propiedades calculadas ----------

    @property
    def torneos_count(self) -> int:
        """Cantidad de torneos asociados a este juego."""
        return len(self.torneos) if self.torneos else 0

    @property
    def registros_count(self) -> int:
        """Cantidad de participaciones registradas en este juego."""
        return len(self.registros) if self.registros else 0

    @property
    def estado_nombre(self) -> str:
        """Nombre legible del estado actual."""
        return self.estado_juego.name if self.estado_juego else "desconocido"

    # ---------- Métodos helper ----------

    def es_activo(self) -> bool:
        """¿El juego está en estado 'estable' o activo?

        Returns:
            bool: True si está disponible para nuevos torneos.
        """
        return self.estado_juego == EstadoJuego.estable

    def obtener_informacion_basica(self) -> dict:
        """Retorna información básica del juego para UI.

        Returns:
            dict: Diccionario con nombre, motor, género, estado.
        """
        return {
            'nombre': self.nombre_juego,
            'motor': self.motor_juego,
            'genero': self.genero_juego,
            'estado': self.estado_nombre,
            'color': self.color_juego,
            'torneos': self.torneos_count,
            'participaciones': self.registros_count
        }

