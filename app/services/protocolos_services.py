from app.db import session
from app.models.protocolos_models import Protocolo


def get_all_protocols():
    return session.query(Protocolo).all()

def get_protocolo_by_id(protocolo_id):
    return session.query(Protocolo).filter_by(id=protocolo_id).first()

def create_protocol(codigo_protocolo,nombre_protocolo,categoria_protocolo,descripcion_protocolo):
    if nombre_protocolo:
        protocolo_existente =session.query(Protocolo).filter_by(nombre=nombre_protocolo).first()
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