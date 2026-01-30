
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base
from app.enums.tipos import EspecialidadRol

from sqlalchemy import Enum as _Enum


class Rol(Base):
    __tablename__ = "roles"
    __table_args__ = {
        "sqlite_autoincrement": True
    }
    
    id_rol : Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre_rol : Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    especialidad_rol:Mapped[EspecialidadRol] = mapped_column(
        _Enum(EspecialidadRol, name="especialidad_rol_enum", values_callable=lambda x: [e.name for e in x]),
        nullable=True,
        default=EspecialidadRol.kinetic_overload,
        server_default=EspecialidadRol.kinetic_overload.name,
        comment='Especialidad o arquetipo neural, define al jugador y su comportamiento en la arena'
    )
    descripcion_rol : Mapped[str] = mapped_column( String(100), nullable=True)
    
    
    def __init__(self,nombre_rol, descripcion_rol, especialidad_rol):
        self.nombre_rol=nombre_rol
        self.descripcion_rol=descripcion_rol
        self.especialidad_rol=especialidad_rol

    def __str__(self):
        return f"{self.nombre_rol} - descripcion: {self.descripcion_rol} - especialidad: {self.especialidad_rol.value[2]}"