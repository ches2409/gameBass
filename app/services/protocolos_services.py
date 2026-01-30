from app.db import session
from app.models.protocolos_models import Protocolo


def get_all_protocols():
    return session.query(Protocolo).all()

def get_protocolo_by_id(protocolo_id):
    return session.query(Protocolo).filter_by(id=protocolo_id).first()