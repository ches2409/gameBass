from app import Equipo
from app.db import session


def get_all_equipos():
    return session.query(Equipo).all()

def get_equipos_by_id(id_equipo):
    return session.query(Equipo).filter_by(id_equipo=id_equipo).first()

def create_equipo(nombre_equipo, lema_equipo, estado_equipo, comandante_equipo):
    
    if not nombre_equipo and not estado_equipo and not comandante_equipo:
        raise ValueError("Faltan campos por completar")
    
    nuevo_equipo = Equipo(
        nombre_equipo=nombre_equipo,
        lema_equipo=lema_equipo,
        estado_equipo=estado_equipo,
        comandante_equipo=comandante_equipo
    )
    
    session.add(nuevo_equipo)
    session.commit()
    
    return nuevo_equipo

def update_equipo(id_equipo, nombre_equipo, lema_equipo, estado_equipo, comandante_equipo):
    
    equipo_existente = get_equipos_by_id(id_equipo)
    
    if not equipo_existente:
        raise ValueError("Equipo no encontrado")
    
    equipo_existente.nombre_equipo = nombre_equipo
    equipo_existente.lema_equipo = lema_equipo
    equipo_existente.estado_equipo = estado_equipo
    equipo_existente.comandante_equipo = comandante_equipo
    
    session.commit()
    
    return equipo_existente

def delete_equipo(id_equipo):
    
    equipo = get_equipos_by_id(id_equipo)
    
    if not equipo:
        raise ValueError("Equipo no encontrado")
    
    session.delete(equipo)
    session.commit()
    
    return True