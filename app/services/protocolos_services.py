from app.db import session
from app.models.protocolos_models import Protocolo


def get_all_protocols():
    return session.query(Protocolo).all()

def get_protocolo_by_id(id_protocolo):
    return session.query(Protocolo).filter_by(id_protocolo=id_protocolo).first()

def create_protocol(codigo_protocolo,nombre_protocolo,categoria_protocolo,descripcion_protocolo):
    if nombre_protocolo:
        
        protocolo_existente =session.query(Protocolo).filter_by(nombre_protocolo=nombre_protocolo).first()
        if protocolo_existente:
            raise ValueError(f"Protocolo - {protocolo_existente} - ya existe")
    
    new_protocol = Protocolo(
        codigo_protocolo = codigo_protocolo,
        nombre_protocolo = nombre_protocolo,
        categoria_protocolo = categoria_protocolo,
        descripcion_protocolo = descripcion_protocolo
    )
    
    session.add(new_protocol)
    session.commit()
    
    return new_protocol

def update_protocol(id_protocolo, codigo_protocolo,nombre_protocolo,categoria_protocolo,descripcion_protocolo):
    protocolo=get_protocolo_by_id(id_protocolo)
    
    if not protocolo:
        raise ValueError(f"Protocolo - {protocolo} - no existe")
    
    protocolo.codigo_protocolo=codigo_protocolo
    protocolo.nombre_protocolo=nombre_protocolo
    protocolo.categoria_protocolo=categoria_protocolo
    protocolo.descripcion_protocolo=descripcion_protocolo
    
    session.commit()
    
    return protocolo

def delete_protocolo(id_protocolo):
    protocolo=get_protocolo_by_id(id_protocolo)
    
    session.delete(protocolo)
    
    session.commit()
    
    return True