from sqlalchemy import Integer, String, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, List

from app.db import Base
from app.enums.tipos import EstadoTorneo

from sqlalchemy import Enum as _Enum

if TYPE_CHECKING:
    from .juegos_models import Juego
    from .registros_models import Registro
    from .resultados_models import Resultado


class Torneo(Base):
    __tablename__ = "torneos"
    __table_args__ = {
        "sqlite_autoincrement": True,
        "comment": "Orquesta la disponibilidad de los torneos",
    }

    id_torneo: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre_torneo: Mapped[str] = mapped_column(String(50), nullable=False)
    recompensa_torneo: Mapped[str] = mapped_column(String(50), nullable=False)
    nivel_acceso_min: Mapped[int] = mapped_column(Integer, nullable=False)
    estado_torneo: Mapped[EstadoTorneo] = mapped_column(
        _Enum(
            EstadoTorneo,
            name="estado_torneo_enum",
            nullable=False,
            default=EstadoTorneo.draft,
            server_default="draft",
        )
    )
    max_competidores: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="capacidad maxima de sujetos o equipos en el torneo",
    )
    fecha_creacion: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="fecha de creacion del torneo",
    )
    fecha_inicio: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), comment="fecha de inicio del torneo"
    )
    fecha_fin: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), comment="fecha de fin del torneo"
    )

    # --- Clave Foránea (Foreign Key) ---
    # Esta columna vincula el torneo con un juego.
    id_juego: Mapped[int] = mapped_column(ForeignKey("juegos.id_juego"), nullable=False)

    # --- Relaciones ---
    # Relación 1:N con Registro (muchos)
    registros: Mapped[List["Registro"]] = relationship(
        "Registro", back_populates="torneo", cascade="all, delete-orphan"
    )
    # Relación 1:N con resultados (muchos) - (El cuadro de honor del torneo)
    resultados: Mapped[List["Resultado"]] = relationship(
        "Resultado", back_populates="torneo"
    )

    # Permite acceder al objeto Juego desde una instancia de Torneo (ej: mi_torneo.juego)
    juego: Mapped["Juego"] = relationship("Juego", back_populates="torneos")

    def __repr__(self) -> str:
        return f"<Torneo(id={self.id_torneo}, nombre='{self.nombre_torneo}', estado='{self.estado_torneo.name}')>"
