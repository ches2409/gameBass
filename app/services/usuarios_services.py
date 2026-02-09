from app import Usuario
from app.db import session


def get_all_usuarios():
    return session.query(Usuario).all()

def get_usuarios_by_id(id_usuario):
    return session.query(Usuario).filter_by(id_usuario=id_usuario).first()

def create_usuario(alias_usuario, email_usuario, id_jerarquia):
    
    if not all ([alias_usuario, email_usuario, id_jerarquia]):
        raise ValueError("Alias, email y jerarquia son campos obligatorios")
    
    try:
        id_jerarquia_int = int(id_jerarquia)
    except ValueError as e:
        raise TypeError(f"Dato de entrada inválido: {e}")
    
    nuevo_usuario = Usuario(
        alias_usuario=alias_usuario,
        email_usuario=email_usuario,
        id_jerarquia=id_jerarquia_int
    )
    
    session.add(nuevo_usuario)
    session.commit()
    
    return nuevo_usuario

def update_usuario(id_usuario, alias_usuario, email_usuario, id_jerarquia):
    usuario = get_usuarios_by_id(id_usuario)
    
    if not usuario:
        raise ValueError("Usuario no encontrado")
    
    try:
        if alias_usuario is not None:
            usuario.alias_usuario = alias_usuario
        if email_usuario is not None:
            usuario.email_usuario = email_usuario
        if id_jerarquia is not None:
            usuario.id_jerarquia = int(id_jerarquia)
    except (KeyError, ValueError) as e:
        session.rollback()
        raise TypeError(f"Dato de entrada inválido al actualizar: {e}")
    
    session.commit()
    
    return usuario

def delete_usuario(id_usuario):
    usuario = get_usuarios_by_id(id_usuario)
    
    if not usuario:
        raise ValueError("Usuario no encontrado")
    
    session.delete(usuario)
    session.commit()
    
    return True