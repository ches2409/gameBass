from sqlalchemy import Integer, String, func, Enum as _Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING

from app.db import Base
from app.enums.tipos import EstadoJuego

if TYPE_CHECKING:
    from .torneos_models import Torneo

class Juego(Base):
    __tablename__ = 'juegos'
    __table_args__ = {
        "sqlite_autoincrement": True,
        "comment": "Almacena los juegos disponibles para torneos"
    }

    id_juego: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre_juego: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    motor_juego: Mapped[str] = mapped_column(String(50), nullable=False)
    genero_juego: Mapped[str] = mapped_column(String(50), nullable=False)
    estado_juego: Mapped[EstadoJuego] = mapped_column(
        _Enum(
            EstadoJuego,
            name="estado_juego_enum",
            default=EstadoJuego.estable,
            server_default="estable"
        )
    )
    color_juego: Mapped[str] = mapped_column(String(7), default="#ffffff")

    # --- Relación hacia los "Muchos" (Torneos) ---
    # Esto crea una colección de objetos Torneo en cada instancia de Juego.
    torneos: Mapped[List["Torneo"]] = relationship(
        "Torneo", 
        back_populates="juego", 
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Juego(id={self.id_juego}, nombre='{self.nombre_juego}')>"