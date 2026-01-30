from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base
from app.enums.tipos import CategoriaProtocolo

from sqlalchemy import Enum as _Enum


class Protocolo(Base):
    __tablename__ = "Protocolos"
    __table_args__ = {
        "sqlite_autoincrement": True,
    }
    
    id_protocolo : Mapped[int] = mapped_column(Integer, primary_key=True)
    codigo_protocolo : Mapped[str] = mapped_column(String(20),nullable=False)
    nombre_protocolo : Mapped[str] = mapped_column(String(50), nullable=False)
    categoria_protocolo : Mapped[CategoriaProtocolo] = mapped_column(
        _Enum(CategoriaProtocolo, name="caategoria_protocolo_enum"),
        nullable=False,
        default=CategoriaProtocolo.user,
        server_default="user"
    )
    descripcion_protocolo : Mapped[str] = mapped_column(String(200), nullable=False)