from datetime import datetime
from app import Torneo
from app.db import session
from app.enums.tipos import EstadoTorneo


def get_all_torneos():
    return session.query(Torneo).all()

def get_torneos_by_id(id_torneo):
    return session.query(Torneo).filter_by(id_torneo=id_torneo).first()

def create_torneo(nombre_torneo, recompensa_torneo, estado_torneo, max_competidores, fecha_inicio, fecha_fin, id_juego):
    
    # 1. Validación de datos de entrada
    if not all([nombre_torneo, recompensa_torneo, estado_torneo, max_competidores, fecha_inicio, fecha_fin, id_juego]):
        raise ValueError("Todos los campos son obligatorios.")

    # 2. Conversión de tipos (la causa del error original)
    try:
        fecha_inicio_dt = datetime.fromisoformat(fecha_inicio)
        fecha_fin_dt = datetime.fromisoformat(fecha_fin)
        estado_enum = EstadoTorneo[estado_torneo]
        max_competidores_int = int(max_competidores)
        id_juego_int = int(id_juego)
    except (KeyError, ValueError) as e:
        raise TypeError(f"Dato de entrada inválido: {e}")
    
    # 3. Creación del objeto
    new_torneo=Torneo(
        nombre_torneo=nombre_torneo,
        recompensa_torneo=recompensa_torneo,
        estado_torneo=estado_enum,
        max_competidores=max_competidores_int,
        fecha_inicio=fecha_inicio_dt,
        fecha_fin=fecha_fin_dt,
        id_juego=id_juego_int
    )
    session.add(new_torneo)
    session.commit()
    
    return new_torneo

def update_torneo(id_torneo, nombre_torneo, recompensa_torneo, estado_torneo, max_competidores, fecha_inicio, fecha_fin, id_juego):
    torneo=get_torneos_by_id(id_torneo)
    
    if not torneo:
        raise ValueError(f"El torneo con ID {id_torneo} no existe.")
    
    # Actualiza solo los campos que se proporcionan
    if nombre_torneo is not None:
        torneo.nombre_torneo = nombre_torneo
    if recompensa_torneo is not None:
        torneo.recompensa_torneo = recompensa_torneo
    if estado_torneo is not None:
        torneo.estado_torneo = EstadoTorneo[estado_torneo]
    if max_competidores is not None:
        torneo.max_competidores = int(max_competidores)
    if fecha_inicio is not None:
        torneo.fecha_inicio = datetime.fromisoformat(fecha_inicio)
    if fecha_fin is not None:
        torneo.fecha_fin = datetime.fromisoformat(fecha_fin)
    if id_juego is not None:
        torneo.id_juego = int(id_juego)
    
    session.commit()
    
    return torneo

def delete_torneo(id_torneo):
    torneo=get_torneos_by_id(id_torneo)
    
    if not torneo:
        raise ValueError(f"El torneo con ID {id_torneo} no existe.")
    
    session.delete(torneo)
    session.commit()
    
    return True