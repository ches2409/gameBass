
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base


class Rol(Base):
    __tablename__ = "roles"
    __table_args__ = {
        "sqlite_autoincrement": True
    }
    
    id_rol : Mapped[int] = mapped_column(Integer, primary_key=True)
    # Cambiamos a String para permitir roles personalizados (ej: 'SuperAdmin')
    nombre_rol : Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    descripcion_rol : Mapped[str] = mapped_column(String(100), nullable=True)
    
    
    def __init__(self,nombre_rol, descripcion_rol):
        self.nombre_rol=nombre_rol
        self.descripcion_rol=descripcion_rol

    def __str__(self):
        return f"{self.nombre_rol} - {self.descripcion_rol}"