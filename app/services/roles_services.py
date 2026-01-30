from app.db import session
from app.models.roles_models import Rol


def get_all_roles():
    return session.query(Rol).all()

def get_roles_by_id(rol_id):
    return session.query(Rol).get(rol_id)

def create_rol(nombre, descripcion_rol, especialidad_rol):
    
    
    if nombre:
        
        # Verificar si el rol existe
        rol_existente = session.query(Rol).filter_by(nombre_rol=nombre).first()
        if rol_existente:
            raise ValueError(f"El Rol {nombre} ya esta creado")
        
        new_rol = Rol(
            nombre_rol=nombre,
            descripcion_rol=descripcion_rol,
            especialidad_rol=especialidad_rol
        )
        session.add(new_rol)
        session.commit()
        return new_rol
    
    return False