"""Modelo de Usuario - Autenticación e identidad del sistema.

Define usuarios con credenciales seguras, jerarquías de permisos, y relaciones
con equipos, torneos y resultados.
"""

from sqlalchemy import Integer, String, DateTime, ForeignKey, CheckConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_login import UserMixin
from typing import List, TYPE_CHECKING, Optional

from app.db import Base

if TYPE_CHECKING:
    from app.models.jerarquias_models import Jerarquia
    from app.models.equipos_models import Equipo
    from app.models.registros_models import Registro
    from app.models.resultados_models import Resultado


class Usuario(Base, UserMixin):
    """Representa un usuario autenticado del sistema.
    
    Usuario contiene:
        - Credenciales: alias único y email
        - Autenticación: contraseña hasheada
        - Identificación: foto/avatar
        - Rol: jerarquía con permisos
        - Participación: equipos que comanda y en los que es miembro
        - Competencias: registros de torneos y resultados
    """

    __tablename__ = "usuarios"
    
    __table_args__ = (
        CheckConstraint(
            'length(alias_usuario) >= 3',
            name='check_alias_usuario_minlen'
        ),
        CheckConstraint(
            'email_usuario LIKE ''%@%''',
            name='check_email_usuario_format'
        ),
        CheckConstraint(
            'length(password_usuario) >= 60',
            name='check_password_usuario_minlen'
        ),
        {
            "sqlite_autoincrement": True,
            "comment": "Usuarios autenticados del sistema"
        },
    )

    id_usuario: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    alias_usuario: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
        comment="Nick único del usuario (mínimo 3 caracteres)"
    )

    email_usuario: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
        comment="Email único (debe contener @)"
    )

    password_usuario: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Contraseña hasheada (mínimo 60 caracteres con werkzeug)"
    )

    foto_usuario: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="URL o path del avatar"
    )

    creacion_usuario: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="Fecha de creación de la cuenta"
    )

    id_jerarquia: Mapped[int] = mapped_column(
        ForeignKey("jerarquias.id_jerarquia", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="ID de la jerarquía del usuario"
    )

    # Relaciones
    jerarquia: Mapped["Jerarquia"] = relationship(
        "Jerarquia",
        back_populates="usuarios"
    )

    registros: Mapped[List["Registro"]] = relationship(
        "Registro",
        back_populates="usuario",
        cascade="all, delete-orphan"
    )

    resultados: Mapped[List["Resultado"]] = relationship(
        "Resultado",
        back_populates="usuario"
    )

    equipos_comandados: Mapped[List["Equipo"]] = relationship(
        "Equipo",
        back_populates="comandante"
    )

    membresias: Mapped[List["Equipo"]] = relationship(
        "Equipo",
        secondary="miembros_equipo",
        back_populates="miembros"
    )

    def __repr__(self) -> str:
        """Representación técnica para debugging."""
        jerarquia_name = self.jerarquia.nombre_jerarquia if self.jerarquia else "None"
        return (
            f"<Usuario(id={self.id_usuario}, "
            f"alias='{self.alias_usuario}', "
            f"jerarquia='{jerarquia_name}')>"
        )

    def __str__(self) -> str:
        """Representación amigable para UI."""
        return self.alias_usuario

    @property
    def equipos_count(self) -> int:
        """Cantidad de equipos que comanda."""
        return len(self.equipos_comandados) if self.equipos_comandados else 0

    @property
    def membresias_count(self) -> int:
        """Retorna la cantidad de equipos en los que el usuario es miembro."""
        return len(self.membresias) if self.membresias else 0

    @property
    def resultados_count(self) -> int:
        """Retorna la cantidad de resultados (podios) obtenidos por el usuario."""
        return len(self.resultados) if self.resultados else 0

    def get_id(self) -> str:
        """Retorna ID como string para Flask-Login."""
        return str(self.id_usuario)

    def puede_comandar_equipo(self, equipo_id: int) -> bool:
        """¿Usuario comanda este equipo?
        
        Args:
            equipo_id (int): ID del equipo.
        
        Returns:
            bool: True si lo comanda.
        
        Raises:
            TypeError: Si equipo_id no es int.
        """
        if not isinstance(equipo_id, int):
            raise TypeError(f"equipo_id debe ser int, recibido {type(equipo_id)}")
        return any(e.id_equipo == equipo_id for e in self.equipos_comandados)

    def es_miembro_equipo(self, equipo_id: int) -> bool:
        """¿Usuario es miembro de este equipo?
        
        Args:
            equipo_id (int): ID del equipo.
        
        Returns:
            bool: True si es miembro.
        
        Raises:
            TypeError: Si equipo_id no es int.
        """
        if not isinstance(equipo_id, int):
            raise TypeError(f"equipo_id debe ser int, recibido {type(equipo_id)}")
        return any(e.id_equipo == equipo_id for e in self.membresias)

    def obtener_nivel_acceso(self) -> int:
        """Obtiene nivel numérico de acceso (0-100)."""
        return self.jerarquia.nivel_acceso if self.jerarquia else 0
