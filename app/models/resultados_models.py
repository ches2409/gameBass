from sqlalchemy import Integer, Boolean, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import TYPE_CHECKING

from app.db import Base

if TYPE_CHECKING:
    from app.models.torneos_models import Torneo
    from app.models.usuarios_models import Usuario
    from app.models.equipos_models import Equipo


class Resultado(Base):
    __tablename__ = 'resultados'
    __table_args__ = {
        "sqlite_autoincrement":True,
        "comment":"Almacena el podio y las estadisticas de cada torneo"
    }
    
    id_resultado : Mapped[int] = mapped_column(Integer, primary_key=True)
    # Metricas finales
    posicion_final:Mapped[int] = mapped_column(Integer, nullable=False, comment="Lugar en el podio '1,2,3...'")
    puntaje_total:Mapped[int] = mapped_column(Integer, nullable=False, comment="Suma de todos los registros del torneo")
    victoria_confirmada:Mapped[bool] = mapped_column(Boolean, default=False)
    recompensa_entregada:Mapped[str] = mapped_column(String(100), nullable=True)
    
    # --- Vinculos ---
    id_torneo:Mapped[int] = mapped_column(ForeignKey('torneos.id_torneo'), ondelete="SET NULL")
    id_usuario:Mapped[int] = mapped_column(ForeignKey('usuarios.id_usuario'), nullable=False)
    id_equipo:Mapped[int] = mapped_column(ForeignKey('equipos.id_equipo'), nullable=True)
    
    # --- Relaciones ---
    torneo:Mapped["Torneo"]=relationship("Torneo", back_populates="resultados")
    usuario:Mapped["Usuario"]=relationship("Usuario", back_populates="resultados")
    equipo:Mapped["Equipo"]=relationship("Equipo", back_populates="resultados")
