from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Sujeto(Base):
    __tablename__ = 'sujetos'
    __table_args__ = {
        'sqlite_autoincrement': True,
        'comment': 'crea registros de cada jugador  (sujeto_neural)'
    }
    id_sujeto : Mapped[int] = mapped_column(Integer,primary_key=True)
    codename_tag : Mapped[String] = mapped_column(String(50), comment='nombre de jugador')
    uplink_neural : Mapped[str] = mapped_column(String(50), comment='direccion de correo electronico')
    
    lethal_index : Mapped[int] = mapped_column(Integer,comment='indice de letalidad, mide eficiencia del sujeto y su probalidad de ser desconectado')
    sync_ratio : Mapped[int] = mapped_column(Integer,comment='mide la integridad de la conexion del jugador')