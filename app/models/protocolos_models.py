"""Modelo de Protocolo - Reglas normativas del sistema.

Define los protocolos que rigen el comportamiento fundamental del ecosistema.

Protocolos representan:
- Reglas de acceso: quién puede hacer qué (ADMIN, MOD, USER, etc.)
- Políticas de data: cómo se gestionan datos sensibles
- Capacidades críticas: permisos especiales del sistema
- Auditoría y compliance: qué acciones se registran

Características:
- Cada protocolo tiene código único (ARN_BUILD, ADMIN_LOCK, etc.)
- Se vinculan a Jerarquías (roles) mediante relación M:N
- Inmutables una vez creados (solo se archivan)
- Determinan el alcance completo de permisos de una jerarquía

Ejemplo:
    >>> protocolo = Protocolo(
    ...     codigo_protocolo=CodigoProtocolo.arn_build,
    ...     nombre_protocolo="Construcción ARN",
    ...     categoria_protocolo=CategoriaProtocolo.admin,
    ...     descripcion_protocolo="Permite construir y modificar estructuras ARN"
    ... )
    >>> session.add(protocolo)
    >>> session.commit()
"""

from sqlalchemy import Integer, String, Enum as _Enum, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, List, Optional

from app.db import Base
from app.enums.tipos import CategoriaProtocolo, CodigoProtocolo

if TYPE_CHECKING:
    from app.models.jerarquias_models import Jerarquia


class Protocolo(Base):
    """Protocolo de acceso y capacidades del sistema.
    
    Un Protocolo encapsula:
        - Código único: identificador único (ej: ARN_BUILD)
        - Nombre: descripción breve (ej: "Construcción ARN")
        - Categoría: nivel de riesgo (admin, moderator, user, guest)
        - Descripción: explicación del permiso
    
    Los protocolos son reglas de negocio inmutables. Define qué acción
    puede hacer qué tipo de usuario. Se vinculan a Jerarquías (roles)
    mediante relación N:N a través de tabla "jerarquia_protocolo".
    
    Ejemplo de flujo:
        Protocolo ARN_BUILD → vinculado a Jerarquía ADMIN
                           → vinculado a Jerarquía DEVELOPER
                       ❌  No vinculado a Jerarquía USER
    
    Resultado: Solo admins y developers pueden construir ARN.
    """
    
    __tablename__ = "protocolos"
    
    __table_args__ = (
        CheckConstraint('length(nombre_protocolo) >= 3', name='check_nombre_protocolo_min'),
        CheckConstraint('length(descripcion_protocolo) >= 10', name='check_descripcion_protocolo_min'),
        {
            "sqlite_autoincrement": True,
            "comment": "Protocolos (reglas): códigos, permisos, capacidades críticas"
        },
    )
    
    # ===== Primary Key =====
    id_protocolo: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # ===== Identificadores Únicos =====
    codigo_protocolo: Mapped[CodigoProtocolo] = mapped_column(
        _Enum(
            CodigoProtocolo,
            name="codigo_protocolo_enum",
            values_callable=lambda x: [e.name for e in x]
        ),
        nullable=False,
        unique=True,
        index=True,
        default=CodigoProtocolo.arn_build,
        server_default=CodigoProtocolo.arn_build.name,
        comment="Código único del protocolo (ej: ARN_BUILD, ADMIN_LOCK)"
    )
    
    # ===== Atributos Descriptivos =====
    nombre_protocolo: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Nombre del protocolo (ej: 'Construcción ARN')"
    )
    
    categoria_protocolo: Mapped[CategoriaProtocolo] = mapped_column(
        _Enum(
            CategoriaProtocolo,
            name="categoria_protocolo_enum",
            values_callable=lambda x: [e.name for e in x]
        ),
        nullable=False,
        index=True,
        default=CategoriaProtocolo.user,
        server_default=CategoriaProtocolo.user.name,
        comment="Categoría de riesgo/acceso (admin, moderator, user, guest)"
    )
    
    descripcion_protocolo: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Explicación detallada del protocolo y su propósito"
    )
    
    # ===== Relaciones (M:N con Jerarquia) =====
    jerarquias: Mapped[List["Jerarquia"]] = relationship(
        "Jerarquia",
        secondary="jerarquia_protocolo",
        back_populates="protocolos",
        lazy="select"
    )
    
    def __repr__(self) -> str:
        """Representación técnica para debugging."""
        return (
            f"<Protocolo(id={self.id_protocolo}, "
            f"codigo={self.codigo_protocolo.name}, "
            f"nombre='{self.nombre_protocolo}', "
            f"categoria={self.categoria_protocolo.name}, "
            f"jerarquias={len(self.jerarquias)})>"
        )
    
    def __str__(self) -> str:
        """Representación amigable para UI."""
        return f"[{self.codigo_protocolo.name}] {self.nombre_protocolo}"
    
    @property
    def es_critico(self) -> bool:
        """¿Este protocolo requiere privilegios críticos?
        
        Retorna True si es nivel ADMIN o superior.
        """
        return self.categoria_protocolo in [
            CategoriaProtocolo.admin,
            CategoriaProtocolo.system
        ]
    
    @property
    def jerarquias_count(self) -> int:
        """¿Cuántas jerarquías (roles) tienen este protocolo?"""
        return len(self.jerarquias) if self.jerarquias else 0
    
    @property
    def categoria_nombre(self) -> str:
        """Nombre legible de la categoría."""
        return self.categoria_protocolo.name
    
    def obtener_informacion_basica(self) -> dict:
        """Retorna información del protocolo para UI/API."""
        return {
            'id': self.id_protocolo,
            'codigo': self.codigo_protocolo.name,
            'nombre': self.nombre_protocolo,
            'categoria': self.categoria_nombre,
            'descripcion': self.descripcion_protocolo,
            'es_critico': self.es_critico,
            'jerarquias_asignadas': self.jerarquias_count,
            'jerarquias': [j.nombre_jerarquia for j in self.jerarquias] if self.jerarquias else []
        }
    
    def puede_ser_usado_por_jerarquia(self, jerarquia_id: int) -> bool:
        """¿Una jerarquía específica tiene este protocolo?
        
        Args:
            jerarquia_id: ID de la jerarquía a verificar
            
        Returns:
            True si la jerarquía tiene asignado este protocolo
        """
        return any(j.id_jerarquia == jerarquia_id for j in self.jerarquias)
