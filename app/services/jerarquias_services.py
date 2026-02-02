from sqlalchemy import select
from app.db import session
from app.models.jerarquias_models import Jerarquia

def get_all_jerarquias():
    # return session.query(Jerarquia).all()
    
    # Estilo SQLAlchemy 2.0 (Moderno)
    # select(): Construye la consulta
    # scalars(): Obtiene las instancias del modelo limpias de los resultados
    return session.execute(select(Jerarquia)).scalars().all()

def get_jerarquia_by_id(jerarquia_id):
    # RECOMENDACIÓN: Usar session.get() para búsquedas por Primary Key.
    # 1. Es compatible con SQLAlchemy 2.0.
    # 2. Usa el "Identity Map" (caché de sesión) para mayor rendimiento.
    # 3. Devuelve None si no existe (fácil de validar con un if).
    #
    # Nota: Corregimos el error lógico anterior, ya que 'filter_by(id=...)' fallaría
    # porque tu modelo usa 'id_jerarquia', no 'id'.
    return session.get(Jerarquia, jerarquia_id)

def create_jerarquia(nombre_jerarquia, subtitulo_jerarquia,descripcion_jerarquia, nivel_acceso,protocolos):

    if nombre_jerarquia:
        # 1. Verificar la existencia
        jerarquia_existente = (
            session.query(Jerarquia)
            .filter_by(nombre_jerarquia=nombre_jerarquia)
            .first()
        )
        # Estilo 2.0: Usamos select() + where()
        # Es más explícito y consistente con el resto de consultas modernas
        # stmt = select(Jerarquia).where(Jerarquia.nombre_jerarquia == nombre_jerarquia)
        # jerarquia_existente = session.execute(stmt).scalars().first()

        if jerarquia_existente:
            raise Exception(f"Jerarquia { nombre_jerarquia } ya existe!")
        
        # 2. Crear instancia
        new_jerarquia = Jerarquia(
            nombre_jerarquia=nombre_jerarquia,
            subtitulo_jerarquia=subtitulo_jerarquia,
            descripcion_jerarquia=descripcion_jerarquia,
            nivel_acceso=nivel_acceso,
            protocolos=protocolos
        )
        session.add(new_jerarquia)
        session.commit()
        
        # 3. Retornamos el objeto completo (ahora tiene ID asignado)
        return new_jerarquia
    
    return None

def update_jerarquia(id_jerarquia, nombre_jerarquia, subtitulo_jerarquia, descripcion_jerarquia, nivel_acceso, protocolos):
    
    jerarquia=get_jerarquia_by_id(id_jerarquia)
    
    if not jerarquia:
        raise ValueError(f"La jerarquia {id_jerarquia} no existe!")
    
    jerarquia.nombre_jerarquia = nombre_jerarquia
    jerarquia.subtitulo_jerarquia = subtitulo_jerarquia
    jerarquia.descripcion_jerarquia = descripcion_jerarquia
    jerarquia.nivel_acceso = nivel_acceso
    jerarquia.protocolos = protocolos
    
    session.commit()
    
    return jerarquia

def delete_jerarquia(id_jerarquia):
    jerarquia=get_jerarquia_by_id(id_jerarquia)
    
    # Validación: Si no existe, no podemos borrarlo
    if not jerarquia:
        return False
    
    session.delete(jerarquia)
    
    session.commit()
    
    return True
