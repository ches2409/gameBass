from app import Torneo
from app.db import session


def get_all_torneos():
    return session.query(Torneo).all()

def get_torneos_by_id(id_torneo):
    return session.query(Torneo).filter_by(id_torneo=id_torneo).first()

def create_torneo(nombre_torneo, recompensa_torneo, estado_torneo, max_competidores, fecha_inicio, fecha_fin, id_juego):
    
    if not nombre_torneo:
        raise ValueError("El nombre del torneo es obligatorio.")
    
    new_torneo=Torneo(
        nombre_torneo=nombre_torneo,
        recompensa_torneo=recompensa_torneo,
        estado_torneo=estado_torneo,
        max_competidores=max_competidores,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        id_juego=id_juego
    )
    session.add(new_torneo)
    session.commit()
    
    return new_torneo

def update_torneo(id_torneo, nombre_torneo, recompensa_torneo, estado_torneo, max_competidores, fecha_inicio, fecha_fin, id_juego):
    torneo=get_torneos_by_id(id_torneo)
    
    if not torneo:
        raise ValueError(f"El torneo con ID {id_torneo} no existe.")
    
    torneo.nombre_torneo = nombre_torneo
    torneo.recompensa_torneo = recompensa_torneo
    torneo.estado_torneo = estado_torneo
    torneo.max_competidores = max_competidores
    torneo.fecha_inicio = fecha_inicio
    torneo.fecha_fin = fecha_fin
    torneo.id_juego = id_juego
    
    session.commit()
    
    return torneo

def delete_torneo(id_torneo):
    torneo=get_torneos_by_id(id_torneo)
    
    if not torneo:
        raise ValueError(f"El torneo con ID {id_torneo} no existe.")
    
    session.delete(torneo)
    session.commit()
    
    return True