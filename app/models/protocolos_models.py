from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base
from app.enums.tipos import CategoriaProtocolo, CodigoProtocolo
from typing import List

from sqlalchemy import Enum as _Enum

# Nota: No necesitamos importar Jerarquia aqui si usamos strings ("Jerarquia") para la relacion

class Protocolo(Base):
    __tablename__ = "Protocolos"
    __table_args__ = {
        "sqlite_autoincrement": True,
        'comment':' gestionan el comportamiento fundamental del ecosistema'
    }
    
    id_protocolo : Mapped[int] = mapped_column(Integer, primary_key=True)
    codigo_protocolo:Mapped[CodigoProtocolo] = mapped_column(
        _Enum(CodigoProtocolo, name="codigo_protocolo_enum", values_callable=lambda x:[e.name for e in x]),
        nullable=False,
        default=CodigoProtocolo.arn_build,
        server_default=CodigoProtocolo.arn_build.name,
        comment="representan las capacidades críticas de administración del Mainframe"
        
    )
    nombre_protocolo : Mapped[str] = mapped_column(String(50), nullable=False)
    categoria_protocolo : Mapped[CategoriaProtocolo] = mapped_column(
        _Enum(CategoriaProtocolo, name="categoria_protocolo_enum"),
        nullable=False,
        default=CategoriaProtocolo.user,
        server_default="user"
    )
    descripcion_protocolo : Mapped[str] = mapped_column(String(200), nullable=False)

    # Relación inversa (opcional pero recomendada para navegación bidireccional)
    # secondary: se pasa como string porque la tabla está en otro archivo (jerarquias_models)
    jerarquias: Mapped[List["Jerarquia"]] = relationship(
        "Jerarquia",
        secondary="jerarquia_protocolo",
        back_populates="protocolos"
    )