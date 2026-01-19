import enum

class RolUsuario(enum.Enum):
    administrador="administrador"
    participante="participante"
    preparador="preparador"

class TipoTorneo(enum.Enum):
    puntos="puntos"
    tiempo="tiempo"
    eliminacion="eliminacion"

class EstadoTorneo(enum.Enum):
    pendiente="pendiente"
    activo="activo"
    finalizado="finalizado"
    cancelado="cancelado"

class EstadoEquipo(enum.Enum):
    activo="activo"
    eliminado="eliminado"

class RolEquipo(enum.Enum):
    capitan="capitan"
    miembro="miembro"

class NivelJugador(enum.Enum):
    amateur="amateur"
    casual="casual"
    experto="experto"

class EstadoParticipacion(enum.Enum):
    activo="activo"
    eliminado="eliminado"