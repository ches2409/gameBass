"""Modelo de Equipo - Contiene lógica de negocio y relaciones.

Define los equipos que participan en las arenas. Un equipo tiene un comandante
único (dueño), miembros, registros de participación y un historial de resultados.

El diseño contempla:
- N:M con usuarios (miembros)
- 1:N con registros y resultados (datos históricos)
- Validaciones de nombre, color y tamaño máximo
- Propiedades para métricas (miembros_count, win_rate, etc.)
- Métodos helper para verificar permisos y administrar miembros

Ejemplo de uso:
    >>> equipo = Equipo(nombre_equipo="Alpha", color_equipo="#FF00FF", id_comandante=1)
    >>> equipo.agregar_miembro(usuario)
    True
    >>> equipo.win_rate
    75.0
"""

from sqlalchemy import (
    Integer,
    String,
    DateTime,
    func,
    ForeignKey,
    Table,
    Column,
    CheckConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as _Enum

from typing import TYPE_CHECKING, List, Optional

from app.db import Base
from app.enums.tipos import EstadoEquipo

if TYPE_CHECKING:
    from app.models.usuarios_models import Usuario
    from app.models.registros_models import Registro
    from app.models.resultados_models import Resultado


# --- Tabla de Asociación (Muchos a Muchos) ---
# Un usuario puede estar en muchos equipos y un equipo tiene muchos usuarios.
miembros_equipo = Table(
    "miembros_equipo",
    Base.metadata,
    Column("id_usuario", Integer, ForeignKey("usuarios.id_usuario"), primary_key=True),
    Column("id_equipo", Integer, ForeignKey("equipos.id_equipo"), primary_key=True),
    Column(
        "fecha_union",
        DateTime(timezone=True),
        server_default=func.now(),
        comment="Momento en que el usuario se une al equipo",
    ),
)


class Equipo(Base):
    """Modelo principal para un equipo dentro de GameBass."""

    __tablename__ = "equipos"
    __table_args__ = (
        CheckConstraint(
            "length(nombre_equipo) >= 3", name="check_nombre_equipo_minlen"
        ),
        CheckConstraint(
            "length(color_equipo) = 7 AND color_equipo LIKE " "#%" "",
            name="check_color_equipo_format",
        ),
        CheckConstraint(
            "maximo_miembros >= 2 AND maximo_miembros <= 100",
            name="check_maximo_miembros_range",
        ),
        {
            "sqlite_autoincrement": True,
            "comment": "Equipos que participan en las competencias",
        },
    )

    id_equipo: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    nombre_equipo: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
        comment="Nombre oficial del equipo (mínimo 3 caracteres)",
    )

    lema_equipo: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="Lema o eslogan del equipo"
    )

    maximo_miembros: Mapped[int] = mapped_column(
        Integer,
        default=2,
        nullable=False,
        comment="Cantidad máxima de integrantes permitida",
    )

    fecha_formacion: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="Fecha de creación del equipo",
    )

    color_equipo: Mapped[str] = mapped_column(
        String(7), nullable=False, comment="Color identificador en formato #RRGGBB"
    )

    estado_equipo: Mapped[EstadoEquipo] = mapped_column(
        _Enum(
            EstadoEquipo,
            name="estado_equipo_enum",
            nullable=False,
            default=EstadoEquipo.pendiente,
            server_default="pendiente",
        ),
        index=True,
    )

    # --- Clave Foránea (Foreign Key) del líder ---
    id_comandante: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id_usuario", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Usuario que comanda/propietario del equipo",
    )

    # --- RELACIONES ---
    comandante: Mapped["Usuario"] = relationship(
        "Usuario", back_populates="equipos_comandados"
    )

    miembros: Mapped[List["Usuario"]] = relationship(
        "Usuario", secondary=miembros_equipo, back_populates="membresias"
    )

    registros: Mapped[List["Registro"]] = relationship(
        "Registro", back_populates="equipo", cascade="all, delete-orphan"
    )

    resultados: Mapped[List["Resultado"]] = relationship(
        "Resultado", back_populates="equipo"
    )

    def __repr__(self) -> str:
        """Representación técnica para debugging."""
        miembros_cnt = len(self.miembros) if self.miembros else 0
        return (
            f"<Equipo(id={self.id_equipo}, "
            f"nombre='{self.nombre_equipo}', "
            f"comandante={self.id_comandante}, "
            f"miembros={miembros_cnt})>"
        )

    def __str__(self) -> str:
        """Representación amigable para UI."""
        return self.nombre_equipo

    # ---------- Propiedades calculadas ----------

    @property
    def miembros_count(self) -> int:
        """Número de usuarios inscritos en el equipo."""
        return len(self.miembros) if self.miembros else 0

    @property
    def registros_count(self) -> int:
        """Cantidad de registros de participación."""
        return len(self.registros) if self.registros else 0

    @property
    def resultados_count(self) -> int:
        """Cantidad de podios obtenidos por el equipo."""
        return len(self.resultados) if self.resultados else 0

    @property
    def win_rate(self) -> float:
        """Porcentaje de victorias calculado sobre resultados."""
        total_jugados = len(self.resultados) if self.resultados else 0
        if total_jugados == 0:
            return 0.0
        victorias = sum(
            1
            for resultado in self.resultados
            if getattr(resultado, "posicion_final", 0) == 1
        )
        return round((victorias / total_jugados) * 100, 1)

    # ---------- Métodos helper / validadores ----------

    def es_comandante(self, usuario_id: int) -> bool:
        """Indica si el usuario dado es el comandante del equipo.

        Args:
            usuario_id (int): ID del supuesto comandante.
        Returns:
            bool: True si coincide con el comandante.
        Raises:
            TypeError: si usuario_id no es int.
        """
        if not isinstance(usuario_id, int):
            raise TypeError(f"usuario_id debe ser int, recibido {type(usuario_id)}")
        return self.id_comandante == usuario_id

    def es_miembro(self, usuario_id: int) -> bool:
        """Comprueba si un usuario es miembro del equipo.

        Args:
            usuario_id (int): ID del usuario a verificar.
        Returns:
            bool: True si está en la lista de miembros.
        Raises:
            TypeError: si usuario_id no es int.
        """
        if not isinstance(usuario_id, int):
            raise TypeError(f"usuario_id debe ser int, recibido {type(usuario_id)}")
        return any(u.id_usuario == usuario_id for u in self.miembros)

    def agregar_miembro(self, usuario: "Usuario") -> bool:
        """Agrega un usuario al equipo si hay espacio y no está ya.

        Args:
            usuario (Usuario): Instancia de Usuario a añadir.
        Returns:
            bool: True si se agregó, False si ya era miembro.
        Raises:
            TypeError: si el argumento no es `Usuario`.
            ValueError: si el equipo ya alcanzó su máximo.
        """
        from app.models.usuarios_models import Usuario as _Usuario

        if not isinstance(usuario, _Usuario):
            raise TypeError("se requiere una instancia de Usuario")
        if self.es_miembro(usuario.id_usuario):
            return False  # ya está
        if self.miembros_count >= self.maximo_miembros:
            raise ValueError("Equipo ya alcanzó su máximo de miembros")
        self.miembros.append(usuario)
        return True

    def remover_miembro(self, usuario: "Usuario") -> bool:
        """Elimina a un usuario de la lista de miembros.

        Args:
            usuario (Usuario): Instancia de Usuario a remover.
        Returns:
            bool: True si se eliminó, False si no era miembro.
        Raises:
            TypeError: si el argumento no es `Usuario`.
        """
        from app.models.usuarios_models import Usuario as _Usuario

        if not isinstance(usuario, _Usuario):
            raise TypeError("se requiere una instancia de Usuario")
        if not self.es_miembro(usuario.id_usuario):
            return False
        self.miembros = [u for u in self.miembros if u.id_usuario != usuario.id_usuario]
        return True
