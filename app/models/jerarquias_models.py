from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Jerarquia(Base):
    __tablename__ = 'jerarquias'
    __table_args__ = {
        "sqlite_autoincrement": True
    }
    
    id_jerarquia : Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre_jerarquia : Mapped[str] = mapped_column(String(50), nullable=False)
    descripcion_jerarquia: Mapped[str] = mapped_column(String(200), nullable=True)
    rango_jerarquia : Mapped[int] = mapped_column(Integer,nullable=False)
    nivel_acceso : Mapped[int] = mapped_column(Integer, nullable=False, comment="")
    
    # permisos
    # protocolos_asignados