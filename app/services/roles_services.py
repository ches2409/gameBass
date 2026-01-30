from app.db import session
from app.models.roles_models import Rol


def get_all_roles():
    return session.query(Rol).all()

def get_roles_by_id(id_rol):
    return session.query(Rol).get(id_rol)

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

def update_rol(id_rol, nombre_rol, descripcion_rol, especialidad_rol):
    rol=get_roles_by_id(id_rol)
    
    if not rol:
        raise ValueError(f"El Rol {nombre_rol} ({id_rol}) no esta creado")
    
    rol.nombre_rol = nombre_rol
    rol.descripcion_rol = descripcion_rol
    rol.especialidad_rol = especialidad_rol
    
    session.commit()
    
    return rol

def delete_rol(id_rol):
    rol=get_roles_by_id(id_rol)
    
    session.delete(rol)
    
    session.commit()
    
    return True