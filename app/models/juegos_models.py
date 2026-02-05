from email.policy import default

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.enums.tipos import EstadoJuego

from sqlalchemy import Enum as _Enum


class Juego(Base):
    __tablename__ = "Juegos"
    __table_args__ = {
        "sqlite_autoincrement": True,
        "comment":"gestiona el catálogo maestro de juegos disponibles en el mainframe"
    }
    id_juego: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre_juego: Mapped[str] = mapped_column(String(50), nullable=False)
    motor_juego: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="nucleo de renderizado del software 'Riot_Kernel'",
    )
    genero_juego: Mapped[str] = mapped_column(String(50), nullable=False)
    estado_juego: Mapped[EstadoJuego] = mapped_column(
        _Enum(
            EstadoJuego,
            name="estado_juego_enum",
            nullable=False,
            default=EstadoJuego.estable,
            server_default="Estable",
        )
    )
    color_juego: Mapped[str] = mapped_column(
        String(7),
        nullable=False,
        default="#A3FF00",
        comment="firma cromatica para la UI y la arena",
    )
