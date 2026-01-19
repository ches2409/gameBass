
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from sqlalchemy import Enum as _Enum

from app.db import Base
from app.enums.tipos import RolUsuario


class Rol(Base):
    __tablename__ = "roles"
    __table_args__ = {
        "sqlite_autoincrement": True,
        "comment": "Crear los roles de los jugadores"
    }
    
    id_rol : Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre_rol : Mapped[RolUsuario] = mapped_column(
        _Enum(RolUsuario,name="rol_usuario_enum"),
        nullable=False,
        default=RolUsuario.participante
    )
    descripcion_rol : Mapped[str] = mapped_column(String(100))
    
    
    def __init__(self,nombre_rol, descripcion_rol):
        self.nombre_rol=nombre_rol
        self.descripcion_rol=descripcion_rol
        
    def __str__(self):
        return f"{self.nombre_rol} - {self.descripcion_rol}"