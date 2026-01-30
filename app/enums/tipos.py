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
    
class EspecialidadRol(enum.Enum):
    frontLine_defense = ("FRONTLINE_DEFENSE", "Resiliencia neural absoluta. Especialista en mitigación de daños y control de presión.","frontLineDefense")
    neural_stealth = ("NEURAL_STEALTH", "Infiltración profunda. Capaz de evadir escaneos de seguridad y eliminación silenciosa.","neuralStealth")
    environment_mastery = ("ENV_MASTERY", "Manipulación del entorno táctico y despliegue de estructuras de soporte neural.","environmentMastery")
    kinetic_overload = ("KINETIC_OVERLOAD", "Máximo daño cinético. Entra en estado de frenesí sacrificando estabilidad por potencia.", "kineticOverload")
    data_foresight =("DATA_FORESIGHT", "Predicción probabilística. Analiza patrones enemigos antes de que ocurran los ataques.","dataForesight")
    system_disruption = ("SYSTEM_DISRUPTION","Guerra electrónica. Especialista en quemar terminales y freír enlaces neurales enemigos.", "systemDisruption")
    neural_restoration = ("NEURAL_RESTORATION", "Recuperación acelerada de integridad del sistema y soporte vital.","neuralRestoration")
    spatial_dislocation = ("SPATIAL_DISLOCATION", "Manipulación de coordenadas locales para movimiento no lineal.","spatialDislocation")
    temporal_lag_infliction = ("TEMPORAL_LAG", "Inducción de latencia forzada en los procesadores enemigos.", "temporalLagInfliction")
    kinetic_absorption = ("KINETIC_ABSORPTION", "Conversión de impacto físico entrante en energía reutilizable.","kineticAbsorption")

    def __init__(self, titulo, descripcion, color):
        self.titulo = titulo
        self.descripcion = descripcion
        self.color = color
    
class CategoriaProtocolo(enum.Enum):
    system ="system"
    user ="user"
    arena ="arena"
    