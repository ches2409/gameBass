from app import Equipo, Usuario
from app.db import session
from app.enums.tipos import EstadoEquipo
from sqlalchemy.orm import selectinload, joinedload
from app.services import usuarios_services


def get_all_equipos():
    """
    Obtiene todos los equipos, precargando eficientemente la lista de miembros
    y la información del comandante para evitar el problema de la consulta N+1.
    """
    return session.query(Equipo).options(
        selectinload(Equipo.miembros).joinedload(Usuario.jerarquia), # Carga miembros y su jerarquía
        selectinload(Equipo.comandante).joinedload(Usuario.jerarquia), # Carga comandante y su jerarquía
        selectinload(Equipo.resultados) # Carga el historial de resultados para calcular el win_rate
    ).all()

def get_equipos_by_id(id_equipo):
    # Optimizamos también esta consulta para que siempre traiga los miembros y el comandante
    return session.query(Equipo).options(
        selectinload(Equipo.miembros),
        joinedload(Equipo.comandante)
    ).filter_by(id_equipo=id_equipo).first()

def create_equipo(nombre_equipo, lema_equipo, maximo_miembros, color_equipo, estado_equipo, id_comandante):
    
    if not all ([nombre_equipo, estado_equipo, id_comandante]):
        raise ValueError("Nombre, estado y comandante son campos obligatorios.")
    
    try:
        estado_enum = EstadoEquipo[estado_equipo]
        id_comandante_int = int(id_comandante)
    except (KeyError, ValueError) as e:
        raise TypeError(f"Dato de entrada inválido: {e}")
    
    nuevo_equipo = Equipo(
        nombre_equipo=nombre_equipo,
        lema_equipo=lema_equipo,
        maximo_miembros=maximo_miembros,
        color_equipo=color_equipo,
        estado_equipo=estado_enum,
        id_comandante=id_comandante_int
    )
    
    # --- PROTOCOLO DE INICIACIÓN DE UNIDAD ---
    # El comandante es, por definición, el primer miembro del equipo.
    # 1. Obtenemos el objeto Usuario del comandante.
    comandante_user = usuarios_services.get_usuarios_by_id(id_comandante_int)
    if comandante_user:
        # 2. Añadimos al comandante a la lista de miembros del nuevo equipo.
        nuevo_equipo.miembros.append(comandante_user)
        
    session.add(nuevo_equipo)
    session.commit()
    
    return nuevo_equipo

def update_equipo(id_equipo, nombre_equipo, lema_equipo,maximo_miembros, color_equipo,estado_equipo, id_comandante):
    
    equipo_existente = get_equipos_by_id(id_equipo)
    
    if not equipo_existente:
        raise ValueError("Equipo no encontrado")
    
    try:
        # Se actualiza solo los campos que se proporcionan, aplicando la conversión de tipos.
        if nombre_equipo is not None:
            equipo_existente.nombre_equipo = nombre_equipo
        if lema_equipo is not None:
            equipo_existente.lema_equipo = lema_equipo
        if maximo_miembros is not None:
            equipo_existente.maximo_miembros = int(maximo_miembros)
        if color_equipo is not None:
            equipo_existente.color_equipo = color_equipo
        if estado_equipo is not None:
            equipo_existente.estado_equipo = EstadoEquipo[estado_equipo]
        if id_comandante is not None:
            equipo_existente.id_comandante = int(id_comandante)
            # Si el comandante cambia, nos aseguramos de que el nuevo comandante esté en la lista de miembros.
            nuevo_comandante = usuarios_services.get_usuarios_by_id(int(id_comandante))
            if nuevo_comandante and nuevo_comandante not in equipo_existente.miembros:
                equipo_existente.miembros.append(nuevo_comandante)

    except (KeyError, ValueError) as e:
        # Si la conversión falla, revertimos la sesión para no dejarla en un estado inconsistente.
        session.rollback()
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

def add_member_to_equipo(id_equipo, id_usuario):
    equipo = get_equipos_by_id(id_equipo)
    usuario = session.query(Usuario).filter_by(id_usuario=id_usuario).first()

    if not equipo or not usuario:
        raise ValueError("Equipo o Usuario no encontrado.")

    if len(equipo.miembros) >= equipo.maximo_miembros:
        raise ValueError(f"El equipo ya ha alcanzado su capacidad máxima de {equipo.maximo_miembros} miembros.")

    if usuario not in equipo.miembros:
        equipo.miembros.append(usuario)
        session.commit()

def remove_member_from_equipo(id_equipo, id_usuario):
    equipo = get_equipos_by_id(id_equipo)
    usuario = session.query(Usuario).filter_by(id_usuario=id_usuario).first()

    if equipo and usuario and usuario in equipo.miembros:
        # No se puede eliminar al comandante del equipo
        if equipo.id_comandante != usuario.id_usuario:
            equipo.miembros.remove(usuario)
            session.commit()