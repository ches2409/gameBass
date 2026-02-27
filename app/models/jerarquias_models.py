"""Modelo de Jerarquías - Gestión de Control de Acceso (RBAC).

Define los niveles de autoridad del sistema (0=PARTICIPANTE, 100=ADMIN) y controla
el acceso a funcionalidades mediante protocolos.
"""

from sqlalchemy import Integer, String, Table, Column, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING, Optional

from app.db import Base

if TYPE_CHECKING:
    from app.models.protocolos_models import Protocolo
    from app.models.usuarios_models import Usuario


jerarquia_protocolo = Table(
    "jerarquia_protocolo",
    Base.metadata,
    Column(
        "id_jerarquia",
        Integer,
        ForeignKey("jerarquias.id_jerarquia", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "id_protocolo",
        Integer,
        ForeignKey("protocolos.id_protocolo", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Jerarquia(Base):
    """Representa un nivel de autoridad en el sistema.

    Niveles estándar:
        - 0: PARTICIPANTE (usuario básico)
        - 40: MOD_TACTICO (moderador de juegos)
        - 60: MOD_ARENA (moderador de competencias)
        - 80: MOD_SISTEMA (administrador general)
        - 100: ADMIN (control total)
    """

    __tablename__ = "jerarquias"

    __table_args__ = (
        CheckConstraint(
            "nivel_acceso >= 0 AND nivel_acceso <= 100",
            name="check_nivel_acceso_valid_range",
        ),
        CheckConstraint(
            "length(nombre_jerarquia) >= 2", name="check_nombre_jerarquia_minlen"
        ),
        CheckConstraint(
            "color_hex IS NULL OR (length(color_hex) = 7 AND color_hex LIKE " "#%" ")",
            name="check_color_hex_format",
        ),
        {
            "sqlite_autoincrement": True,
            "comment": "Niveles de autoridad y control de acceso del sistema",
        },
    )

    id_jerarquia: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    nombre_jerarquia: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
        comment="Nombre único visible (ej: 'OMEGA', 'ADMIN')",
    )

    subtitulo_jerarquia: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="Subtítulo temático (ej: 'THE_SINGULARITY')"
    )

    descripcion_jerarquia: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
        comment="Descripción de facultades y responsabilidades",
    )

    nivel_acceso: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
        comment="Valor 0-100 que determina nivel de autoridad",
    )

    color_hex: Mapped[Optional[str]] = mapped_column(
        String(7),
        nullable=True,
        default="#A3FF00",
        comment="Color identificativo en formato #RRGGBB",
    )

    # Relaciones
    usuarios: Mapped[List["Usuario"]] = relationship(
        "Usuario", back_populates="jerarquia"
    )

    protocolos: Mapped[List["Protocolo"]] = relationship(
        "Protocolo", secondary=jerarquia_protocolo, back_populates="jerarquias"
    )

    def __repr__(self) -> str:
        """Representación técnica para debugging."""
        usuarios_count = len(self.usuarios) if self.usuarios else 0
        return (
            f"<Jerarquia(id={self.id_jerarquia}, "
            f"nombre='{self.nombre_jerarquia}', "
            f"nivel={self.nivel_acceso}, "
            f"usuarios={usuarios_count})>"
        )

    def __str__(self) -> str:
        """Representación amigable para UI."""
        return self.nombre_jerarquia

    # ---------- Propiedades calculadas ----------
    @property
    def color_seguro(self) -> str:
        """Retorna color_hex o default si es None."""
        return self.color_hex if self.color_hex else "#A3FF00"

    @property
    def cantidad_usuarios(self) -> int:
        """Cantidad de usuarios con esta jerarquía."""
        return len(self.usuarios) if self.usuarios else 0

    @property
    def cantidad_protocolos(self) -> int:
        """Cantidad de protocolos asignados."""
        return len(self.protocolos) if self.protocolos else 0

    def es_admin(self) -> bool:
        """¿Nivel ADMIN (máximo control)?"""
        return self.nivel_acceso >= 100

    def es_moderador_sistema(self) -> bool:
        """¿Puede moderar todo el sistema?"""
        return self.nivel_acceso >= 80

    def puede_acceder_a_protocolo(self, protocolo_id: int) -> bool:
        """¿Tiene acceso a protocolo específico?

        Args:
            protocolo_id (int): ID del protocolo a verificar.

        Returns:
            bool: True si tiene acceso.

        Raises:
            TypeError: Si protocolo_id no es int.
        """
        if not isinstance(protocolo_id, int):
            raise TypeError(f"protocolo_id debe ser int, recibido {type(protocolo_id)}")
        return any(p.id_protocolo == protocolo_id for p in self.protocolos)

    def comparar_nivel(self, otro_nivel: int) -> int:
        """Compara este nivel con otro.

        Args:
            otro_nivel (int): Nivel a comparar (0-100).

        Returns:
            int: 1 (mayor), 0 (igual), -1 (menor).

        Raises:
            ValueError: Si otro_nivel no está en rango 0-100.
        """
        if not (0 <= otro_nivel <= 100):
            raise ValueError(
                f"otro_nivel debe estar entre 0-100, recibido {otro_nivel}"
            )

        if self.nivel_acceso > otro_nivel:
            return 1
        elif self.nivel_acceso == otro_nivel:
            return 0
        else:
            return -1

    def obtener_descripcion_nivel(self) -> str:
        """Descripción textual del nivel de acceso para UI."""
        if self.nivel_acceso >= 100:
            return "Administrador (Control Total)"
        elif self.nivel_acceso >= 80:
            return "Moderador de Sistema (Control Completo)"
        elif self.nivel_acceso >= 60:
            return "Moderador de Arena (Gestión de Competencias)"
        elif self.nivel_acceso >= 40:
            return "Moderador Táctico (Gestión de Juegos)"
        else:
            return "Participante (Acceso Básico)"
