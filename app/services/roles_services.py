from app.db import session
from app.models.roles_models import Rol


def get_all_roles():
    return session.query(Rol).all()

def get_roles_by_id(rol_id):
    return session.query(Rol).get(rol_id)

def create_rol(nombre):
    if nombre:
        new_rol = Rol(nombre_rol=nombre)
        # rol_descripcion = Rol(descripcion_rol=descripcion)
        session.add(new_rol)
        # session.add(rol_descripcion)
        session.commit()
        return new_rol
    return False