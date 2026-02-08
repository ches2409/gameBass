from sqlalchemy import Integer, String, DateTime, func, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.enums.tipos import EstadoEquipo

from typing import TYPE_CHECKING, List

from sqlalchemy import Enum as _Enum

if TYPE_CHECKING:
    from app.models.usuarios_models import Usuario
    from app.models.registros_models import Registro
    from app.models.resultados_models import Resultado




# --- Tabla de Asociación (Muchos a Muchos) ---
# Define la tabla intermedia que conecta Usuarios y Equipos.
# Un usuario puede estar en muchos equipos, y un equipo tiene muchos usuarios.
miembros_equipo = Table(
    'miembros_equipo',
    Base.metadata,
    Column('id_usuario', Integer, ForeignKey('usuarios.id_usuario'), primary_key=True),
    Column('id_equipo', Integer, ForeignKey('equipos.id_equipo'), primary_key=True),
    Column('fecha_union', DateTime(timezone=True), server_default=func.now(),comment="Momento en que el sujeto se vincula al equipo")
)

class Equipo(Base):
    __tablename__ = 'equipos'
    __table_args__ = {
        "sqlite_autoincrement":True,
    }

    id_equipo: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre_equipo: Mapped[str] = mapped_column(String(50), nullable=False, comment="nombre oficial del equipo en la arena")
    lema_equipo:Mapped[str] = mapped_column(String(100), nullable=True, comment="lema o firma digital que identifica al equipo")
    fecha_formacion: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="fecha de creación del equipo"
    )
    estado_equipo: Mapped[EstadoEquipo] = mapped_column(
        _Enum(
            EstadoEquipo,
            name="estado_equipo_enum",
            nullable=False,
            default=EstadoEquipo.pendiente,
            server_default="pendiente"
        )
    )

    # --- Clave Foránea (Foreign Key) del lider---
    id_comandante: Mapped[int] = mapped_column(
        ForeignKey('usuarios.id_usuario'),
        nullable=False
    )

    # --- RELACIONES ---
    # 1. El Comandante único (el dueño)
    # --- Relación de Vuelta (Back-reference) ---
    comandante:Mapped["Usuario"]=relationship(
        "Usuario",
        back_populates="equipos_comandados"
    )

    # 2. La lista completa de Miembros (incluye o no al comandante)
    miembros: Mapped[List["Usuario"]] = relationship(
        "Usuario", 
        secondary=miembros_equipo, 
        back_populates="membresias"
    )

    # Relacion 1:N con Registro (muchos)
    registros: Mapped[List["Registro"]] = relationship(
        "Registro",
        back_populates="equipo",
        cascade="all, delete-orphan"
    )

    # Relacion 1:N con Resultado (muchos) - (Historial de podios del equipo)
    resultados: Mapped[List["Resultado"]] = relationship(
        "Resultado",
        back_populates="equipo"
    )

    def __str__(self):
        return f"{self.nombre_equipo}"
