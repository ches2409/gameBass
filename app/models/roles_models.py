"""Modelo de Rol - Arquetipos y especialidades de jugadores.

Define los roles (arquetipos) que un jugador puede asumir dentro de la arena,
tales como tanque, dps, soporte, etc. Cada rol posee una especialidad que
determina su kit de habilidades y comportamiento táctico.

Características:
- Nombre único del rol (ej: "Berserker", "Mágico")
- Especialidad neural que define el arquetipo (ej: kinetic_overload)
- Descripción de responsabilidades y características
- Relación N:1 con Registros (muchos jugadores pueden tomar este rol)

Ejemplo de uso:
    >>> rol = Rol(nombre_rol="Tank", especialidad_rol=EspecialidadRol.armored,
    ...           descripcion_rol="Rol defensivo con alta absorción")
    >>> session.add(rol)
    >>> session.commit()
    >>> rol.registros_count
    42
"""

from typing import List, TYPE_CHECKING, Optional

from sqlalchemy import Integer, String, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as _Enum

from app.db import Base
from app.enums.tipos import EspecialidadRol

if TYPE_CHECKING:
    from app.models.registros_models import Registro


class Rol(Base):
    """Representa un arquetipo de jugador con especialidad única.
    
    Un Rol encapsula:
        - Identidad: nombre único del rol (Guerrero, Mago, etc.)
        - Especialidad: tipo de habilidades (kinetic, elemental, etc.)
        - Descripción: propósito y características del rol
        - Participación: lista de registros (jugadores usando este rol)
    
    El diseño permite reutilizar roles sin duplicarlos y facilita análisis
    de métricas por arquetipo (e.g., win_rate por rol).
    """

    __tablename__ = "roles"

    __table_args__ = (
        CheckConstraint(
            'length(nombre_rol) >= 3',
            name='check_nombre_rol_minlen'
        ),
        CheckConstraint(
            'descripcion_rol IS NULL OR length(descripcion_rol) >= 5',
            name='check_descripcion_rol_minlen'
        ),
        {
            "sqlite_autoincrement": True,
            "comment": "Arquetipos y especialidades de jugadores en la arena"
        },
    )

    id_rol: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    nombre_rol: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
        comment="Nombre único del arquetipo (ej: Guerrero, Mago)"
    )

    especialidad_rol: Mapped[EspecialidadRol] = mapped_column(
        _Enum(
            EspecialidadRol,
            name="especialidad_rol_enum",
            values_callable=lambda x: [e.name for e in x]
        ),
        nullable=False,
        default=EspecialidadRol.kinetic_overload,
        server_default=EspecialidadRol.kinetic_overload.name,
        index=True,
        comment='Especialidad neural del rol (kinetic, elemental, etc.)'
    )

    descripcion_rol: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
        comment="Descripción de capacidades y responsabilidades del rol"
    )

    # --- RELACIONES ---
    # N:1 inversa - Un rol tiene muchos registros (jugadores usando el rol)
    registros: Mapped[List["Registro"]] = relationship(
        "Registro",
        back_populates="rol"
    )

    def __repr__(self) -> str:
        """Representación técnica para debugging."""
        registros_cnt = len(self.registros) if self.registros else 0
        return (
            f"<Rol(id={self.id_rol}, "
            f"nombre='{self.nombre_rol}', "
            f"especialidad='{self.especialidad_rol.name}', "
            f"registros={registros_cnt})>"
        )

    def __str__(self) -> str:
        """Representación amigable para UI."""
        return self.nombre_rol

    # ---------- Propiedades calculadas ----------

    @property
    def registros_count(self) -> int:
        """Cantidad de veces que este rol ha sido utilizado."""
        return len(self.registros) if self.registros else 0

    @property
    def especialidad_nombre(self) -> str:
        """Nombre legible de la especialidad."""
        return self.especialidad_rol.name if self.especialidad_rol else "Desconocida"

    # ---------- Métodos helper ----------

    def obtener_descripcion_completa(self) -> str:
        """Retorna descripción o string por defecto si no tiene.

        Returns:
            str: Descripción del rol o 'Sin descripción' si no existe.
        """
        if not self.descripcion_rol:
            return "Sin descripción"
        return self.descripcion_rol
