from app.db import session
from app.models.jerarquias_models import Jerarquia

def get_all_jerarquias():
    return session.query(Jerarquia).order_by(Jerarquia.nivel_acceso.desc()).all()

def get_jerarquia_by_id(id_jerarquia):
    return session.query(Jerarquia).filter_by(id_jerarquia=id_jerarquia).first()

def create_jerarquia(nombre, subtitulo, descripcion, nivel, protocolos, color):
    if not nombre:
        raise ValueError("El nombre de la jerarquía es obligatorio.")

    new_jerarquia = Jerarquia(
        nombre_jerarquia=nombre,
        subtitulo_jerarquia=subtitulo,
        descripcion_jerarquia=descripcion,
        nivel_acceso=nivel,
        protocolos=protocolos,
        color_hex=color  # <-- Guardamos el color
    )

    session.add(new_jerarquia)
    session.commit()
    return new_jerarquia

def update_jerarquia(id_jerarquia, nombre, subtitulo, descripcion, nivel, protocolos, color):
    jerarquia=get_jerarquia_by_id(id_jerarquia)
    
    if not jerarquia:
        raise ValueError(f"La jerarquia '{nombre}' no existe")
    
    jerarquia.nombre_jerarquia = nombre
    jerarquia.subtitulo_jerarquia = subtitulo
    jerarquia.descripcion_jerarquia = descripcion
    jerarquia.nivel_acceso = nivel
    jerarquia.protocolos = protocolos
    jerarquia.color_hex = color
    
    
    session.commit()
    
    return jerarquia
    

def delete_jerarquia(id_jerarquia):
    jerarquia = get_jerarquia_by_id(id_jerarquia)
    
    if not jerarquia:
        return ValueError(f"La jerarquia '{jerarquia.nombre_jerarquia}' no existe")
    
    session.delete(jerarquia)
    session.commit()
    return True