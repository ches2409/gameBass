from app import Equipo
from app.db import session
from app.enums.tipos import EstadoEquipo


def get_all_equipos():
    return session.query(Equipo).all()

def get_equipos_by_id(id_equipo):
    return session.query(Equipo).filter_by(id_equipo=id_equipo).first()

def create_equipo(nombre_equipo, lema_equipo, estado_equipo, id_comandante):
    
    if not all ([nombre_equipo, estado_equipo, id_comandante]):
        raise ValueError("Nombre, estado y comandante son campos obligatorios")
    
    try:
        estado_enum = EstadoEquipo[estado_equipo]
        id_comandante_int = int(id_comandante)
    except (KeyError, ValueError) as e:
        raise TypeError(f"Dato de entrada inválido: {e}")
    
    nuevo_equipo = Equipo(
        nombre_equipo=nombre_equipo,
        lema_equipo=lema_equipo,
        estado_equipo=estado_enum,
        id_comandante=id_comandante_int
    )
    
    session.add(nuevo_equipo)
    session.commit()
    
    return nuevo_equipo

def update_equipo(id_equipo, nombre_equipo, lema_equipo, estado_equipo, id_comandante):
    
    equipo_existente = get_equipos_by_id(id_equipo)
    
    if not equipo_existente:
        raise ValueError("Equipo no encontrado")
    
    try:
        if nombre_equipo is not None:
            equipo_existente.nombre_equipo = nombre_equipo
        if lema_equipo is not None:
            equipo_existente.lema_equipo = lema_equipo
        if estado_equipo is not None:
            equipo_existente.estado_equipo = estado_equipo
        if id_comandante is not None:
            equipo_existente.id_comandante = id_comandante
    except (KeyError, ValueError) as e:
        raise TypeError(f"Dato de entrada inválido al actualizar: {e}")
    
    session.commit()
    
    return equipo_existente

def delete_equipo(id_equipo):
    
    equipo = get_equipos_by_id(id_equipo)
    
    if not equipo:
        raise ValueError("Equipo no encontrado")
    
    session.delete(equipo)
    session.commit()
    
    return True