from sqlalchemy import Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.jerarquias_models import Jerarquia
    from app.models.equipos_models import Equipo
    from app.models.registros_models import Registro
    from app.models.resultados_models import Resultado


class Usuario(Base):
    __tablename__ = "usuarios"
    __table_args__ = {
        "sqlite_autoincrement": True,
    }

    id_usuario: Mapped[int] = mapped_column(Integer, primary_key=True)
    alias_usuario: Mapped[str] = mapped_column(
        String(50), nullable=False, unique=True, comment="nombre único en la red"
    )
    email_usuario: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        comment="Correo electrónico de contacto",
    )
    password_usuario: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="Contraseña hasheada del usuario"
    )
    foto_usuario: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
        comment="URL completa o nombre de archivo del avatar del usuario",
    )
    creacion_usuario: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    # Crear la llave foranea con Jerarquia
    id_jerarquia: Mapped[int] = mapped_column(
        ForeignKey("jerarquias.id_jerarquia"), nullable=False
    )

    # --- Relaciones ---
    # Relacion de vuelta (Back-Reference)
    jerarquia: Mapped["Jerarquia"] = relationship(
        "Jerarquia", back_populates="usuarios"
    )
    # Relacion 1:N con Registro (muchos)
    registros: Mapped[List["Registro"]] = relationship(
        "Registro", back_populates="usuario", cascade="all, delete-orphan"
    )

    # Relacion 1:N con resultados (muchos) - (Logros personales del sujeto)
    resultados: Mapped[List["Resultado"]] = relationship(
        "Resultado", back_populates="usuario"
    )

    # 1. relación de PROPIEDAD: Equipos que este usuario Fundó/Comanda (1:N)
    equipos_comandados: Mapped[List["Equipo"]] = relationship(
        "Equipo",
        back_populates="comandante",
        # cascade="all, delete-orphan"
    )
    # 2. Relación de MEMBRESÍA: Todos los equipos a los que PERTENECE (M:N)
    membresias: Mapped[List["Equipo"]] = relationship(
        "Equipo", secondary="miembros_equipo", back_populates="miembros"
    )
