from sqlalchemy import Integer, String, Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING

from app.db import Base
# Nota: Usamos string forward reference "Protocolo" para evitar importaciones circulares

if TYPE_CHECKING:
    from app.models.protocolos_models import Protocolo
    

jerarquia_protocolo = Table(
    'jerarquia_protocolo',
    Base.metadata,
    Column('id_jerarquia', Integer, ForeignKey('jerarquias.id_jerarquia'), primary_key=True),
    Column('id_protocolo', Integer, ForeignKey('Protocolos.id_protocolo'), primary_key=True)
)

class Jerarquia(Base):
    __tablename__ = 'jerarquias'
    __table_args__ = {
        "sqlite_autoincrement": True,
        "comment": "Representa la jerarquia de seguridad del sistema (Niveles de acceso)"
    }

    id_jerarquia : Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre_jerarquia : Mapped[str] = mapped_column(String(50), nullable=False, comment="La etiqueta de autoridad visible (ej. 'OMEGA', 'DELTA'). Define la identidad de mando.")
    subtitulo_jerarquia : Mapped[str] = mapped_column(String(50), nullable=False, comment="Un descriptor de 'lore' o técnico (ej. 'THE_SINGULARITY'). Añade profundidad temática a la interfaz.")
    descripcion_jerarquia: Mapped[str] = mapped_column(String(200), nullable=True, comment="Texto extenso que explica las facultades del rango")
    nivel_acceso : Mapped[int] = mapped_column(Integer, nullable=False, comment="Un valor entero (0-100). Define la jerarquía numérica. Se usa para la barra de progreso y lógicas de validación")

    color_hex: Mapped[str] = mapped_column(String(7), nullable=True, default="#A3FF00")

    # Relación de N:M -- protocolos
    # secondary: apunta a la tabla intermedia definida arriba
    # back_populates: debe coincidir con el nombre de la variable en la clase Protocolo
    protocolos: Mapped[List["Protocolo"]] = relationship(
        "Protocolo",
        secondary=jerarquia_protocolo,
        back_populates="jerarquias"
    )
    
    # Relación de 1:N -- usuarios (muchos)
    usuarios: Mapped[List["Usuario"]] = relationship(
        "Usuario",
        back_populates="jerarquia"
    )
    
    def __str__(self):
        return f"{self.nombre_jerarquia}"
    

