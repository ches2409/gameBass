from sqlalchemy import Integer, String, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Registro(Base):
    __tablename__ = 'registros'
    __table_args__ = {
        "sqlite_autoincrement":True,
        "comment":"Caja negra que almacena la telemetría de cada participación en el torneo"
    }
    
    id_registro : Mapped[int] = mapped_column(Integer, primary_key=True)
    
    puntaje:Mapped[int] =mapped_column(Integer, default=0, comment="Resultado númerico de la sesión")
    fecha_registro:Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    
    # --- Vinculos ---
    
    id_torneo:Mapped[int] = mapped_column(
        ForeignKey("torneos.id_torneo"),
        nullable=False,
    )
    id_juego:Mapped[int]=mapped_column(
        ForeignKey("juegos.id_juego"),
        nullable=False,
    )
    id_usuario:Mapped[int]=mapped_column(
        ForeignKey("usuarios.id_usuario"),
        nullable=False,
    )
    
    # --- Competidor ---
    # opcional si es individual, obligatorio si es torneo de equipos
    id_equipo:Mapped[int]=mapped_column(
        ForeignKey("equipos.id_equipo"),
        nullable=True,
    )
    
    # --- Relaciones ---
    torneo:Mapped["Torneo"]=relationship("Torneo", back_populates="registros")
    juego:Mapped["Juego"]=relationship("Juego", back_populates="registros")
    usuario:Mapped["Usuario"]=relationship("Usuario", back_populates="registros")
    equipo:Mapped["Equipo"]=relationship("Equipo", back_populates="registros")
    
