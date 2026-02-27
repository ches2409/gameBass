"""Modelo de Resultado - Podios y rankings de torneos.

Define el resultado final de un usuario o equipo en un torneo específico.
Encapsula:

- Posición final en el podio (1, 2, 3, ...)
- Puntaje acumulado en el torneo
- Estatus de victoria confirmada
- Recompensa entregada

Características:
- Registra SOLO gente en el "podio" (definido por reglamento del torneo)
- Fuente de verdad para rankings y estadísticas
- Immutable (nunca se modifica, solo se crea)
- Auditoría perfecta: usuario siempre está vinculado (RESTRICT)

Ejemplo:
    >>> resultado = Resultado(
    ...     id_usuario=5,
    ...     id_torneo=10,
    ...     posicion_final=1,
    ...     puntaje_total=9500,
    ...     victoria_confirmada=True,
    ...     recompensa_entregada="Medalla de Oro"
    ... )
    >>> session.add(resultado)
    >>> session.commit()
"""

from sqlalchemy import Integer, Boolean, String, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, Optional

from app.db import Base

if TYPE_CHECKING:
    from app.models.torneos_models import Torneo
    from app.models.usuarios_models import Usuario
    from app.models.equipos_models import Equipo


class Resultado(Base):
    """Resultado final de un usuario/equipo en un torneo.
    
    Un Resultado encapsula:
        - Posición en podio: 1 (oro), 2 (plata), 3 (bronce), o más
        - Puntaje total: suma de todos los registros del torneo
        - Confirmación de victoria: flag para auditoría
        - Recompensa: trofeo/medalla/premio entregado
    
    Representa un "hecho histórico" immutable. Los resultados nunca
    se actualizan, solo se crean. Si hay error, se DELETE + INSERT nueva fila.
    
    Relaciones:
        - Puede estar asociado a un Torneo (RESTRICT: no borrar torneo con resultados)
        - Siempre vinculado a Usuario (RESTRICT: no borrar ganador)
        - Opcionalmente vinculado a Equipo (RESTRICT: si equipo ganó, no se borra)
    """
    
    __tablename__ = 'resultados'
    
    __table_args__ = (
        CheckConstraint('posicion_final >= 1', name='check_posicion_final_minimo'),
        CheckConstraint('puntaje_total >= 0', name='check_puntaje_total_no_negativo'),
        {
            "sqlite_autoincrement": True,
            "comment": "Podios y rankings: usuario + torneo + posición + puntaje total"
        },
    )
    
    # ===== Primary Key =====
    id_resultado: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # ===== Métricas Finales =====
    posicion_final: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Lugar en el podio (1=oro, 2=plata, 3=bronce, 4+)"
    )
    
    puntaje_total: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Puntuación acumulada en el torneo (suma de registros)"
    )
    
    victoria_confirmada: Mapped[bool] = mapped_column(Boolean, default=False)
    
    recompensa_entregada: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Trofeo/medalla/premio entregado (ej: 'Medalla de Oro')"
    )
    
    # ===== Vínculos con auditoría (RESTRICT en todos) =====
    id_torneo: Mapped[Optional[int]] = mapped_column(
        ForeignKey('torneos.id_torneo', ondelete="RESTRICT"),
        nullable=True,
        index=True,
        comment="Torneo en el que obtuvo este resultado"
    )
    
    id_usuario: Mapped[int] = mapped_column(
        ForeignKey('usuarios.id_usuario', ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Usuario ganador (RESTRICT: preservar historia)"
    )
    
    id_equipo: Mapped[Optional[int]] = mapped_column(
        ForeignKey('equipos.id_equipo', ondelete="RESTRICT"),
        nullable=True,
        index=True,
        comment="Equipo ganador si aplica (RESTRICT: preservar historia)"
    )
    
    # ===== Relaciones =====
    torneo: Mapped[Optional["Torneo"]] = relationship(
        "Torneo",
        back_populates="resultados"
    )
    
    usuario: Mapped["Usuario"] = relationship(
        "Usuario",
        back_populates="resultados"
    )
    
    equipo: Mapped[Optional["Equipo"]] = relationship(
        "Equipo",
        back_populates="resultados"
    )
    
    def __repr__(self) -> str:
        """Representación técnica para debugging."""
        equipo_str = f", equipo={self.id_equipo}" if self.id_equipo else ""
        medalla = self.obtener_medalla()
        return (
            f"<Resultado(id={self.id_resultado}, "
            f"usuario={self.id_usuario}, "
            f"torneo={self.id_torneo}, "
            f"posicion={self.posicion_final} ({medalla}), "
            f"puntaje={self.puntaje_total}{equipo_str})>"
        )
    
    def __str__(self) -> str:
        """Representación amigable para UI."""
        medalla = self.obtener_medalla()
        equipo_info = f" ({self.equipo.nombre_equipo})" if self.equipo else ""
        return f"#{self.posicion_final} {medalla} - {self.usuario.alias_usuario}{equipo_info}"
    
    @property
    def es_podio(self) -> bool:
        """¿Está en los principales 3 lugares?"""
        return self.posicion_final <= 3
    
    @property
    def es_ganador(self) -> bool:
        """¿Es el campeón (posición 1)?"""
        return self.posicion_final == 1
    
    @property
    def modo(self) -> str:
        """¿Ganó individual o en equipo?"""
        return "Equipo" if self.id_equipo else "Individual"
    
    def obtener_medalla(self) -> str:
        """Retorna la medalla correspondiente a la posición."""
        if self.posicion_final == 1:
            return "🥇 Oro"
        elif self.posicion_final == 2:
            return "🥈 Plata"
        elif self.posicion_final == 3:
            return "🥉 Bronce"
        else:
            return f"4to+ ({self.posicion_final}°)"
    
    def obtener_informacion_basica(self) -> dict:
        """Retorna información del resultado para UI/reportes."""
        return {
            'id': self.id_resultado,
            'usuario': self.usuario.alias_usuario if self.usuario else "Desconocido",
            'torneo': self.torneo.nombre_torneo if self.torneo else "Desconocido",
            'posicion': self.posicion_final,
            'medalla': self.obtener_medalla(),
            'puntaje': self.puntaje_total,
            'equipo': self.equipo.nombre_equipo if self.equipo else "Individual",
            'modo': self.modo,
            'victoria_confirmada': self.victoria_confirmada,
            'recompensa': self.recompensa_entregada,
            'es_podio': self.es_podio,
            'es_ganador': self.es_ganador
        }
