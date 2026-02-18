import enum


class RolUsuario(enum.Enum):
    administrador = "administrador"
    participante = "participante"
    preparador = "preparador"


class TipoTorneo(enum.Enum):
    puntos = "puntos"
    tiempo = "tiempo"
    eliminacion = "eliminacion"


class EstadoTorneo(enum.Enum):
    draft = "draft"
    open = "open"
    live = "live"
    finished = "finished"
    # pendiente = "pendiente"
    # activo="activo"
    # finalizado="finalizado"
    # cancelado="cancelado"


class EstadoEquipo(enum.Enum):
    pendiente = "pendiente"
    activo = "activo"
    inactivo = "inactivo"
    eliminado = "eliminado"


class RolEquipo(enum.Enum):
    capitan = "capitan"
    miembro = "miembro"


class NivelJugador(enum.Enum):
    amateur = "amateur"
    casual = "casual"
    experto = "experto"


class EstadoParticipacion(enum.Enum):
    activo = "activo"
    eliminado = "eliminado"


class EstadoJuego(enum.Enum):
    estable = "estable"
    degraded = "degrade"
    beta = "beta"


class EspecialidadRol(enum.Enum):
    frontLine_defense = (
        "FRONTLINE_DEFENSE",
        "Resiliencia neural absoluta. Especialista en mitigación de daños y control de presión.",
        "frontLineDefense",
    )
    neural_stealth = (
        "NEURAL_STEALTH",
        "Infiltración profunda. Capaz de evadir escaneos de seguridad y eliminación silenciosa.",
        "neuralStealth",
    )
    environment_mastery = (
        "ENV_MASTERY",
        "Manipulación del entorno táctico y despliegue de estructuras de soporte neural.",
        "environmentMastery",
    )
    kinetic_overload = (
        "KINETIC_OVERLOAD",
        "Máximo daño cinético. Entra en estado de frenesí sacrificando estabilidad por potencia.",
        "kineticOverload",
    )
    data_foresight = (
        "DATA_FORESIGHT",
        "Predicción probabilística. Analiza patrones enemigos antes de que ocurran los ataques.",
        "dataForesight",
    )
    system_disruption = (
        "SYSTEM_DISRUPTION",
        "Guerra electrónica. Especialista en quemar terminales y freír enlaces neurales enemigos.",
        "systemDisruption",
    )
    neural_restoration = (
        "NEURAL_RESTORATION",
        "Recuperación acelerada de integridad del sistema y soporte vital.",
        "neuralRestoration",
    )
    spatial_dislocation = (
        "SPATIAL_DISLOCATION",
        "Manipulación de coordenadas locales para movimiento no lineal.",
        "spatialDislocation",
    )
    temporal_lag_infliction = (
        "TEMPORAL_LAG",
        "Inducción de latencia forzada en los procesadores enemigos.",
        "temporalLagInfliction",
    )
    kinetic_absorption = (
        "KINETIC_ABSORPTION",
        "Conversión de impacto físico entrante en energía reutilizable.",
        "kineticAbsorption",
    )

    def __init__(self, titulo, descripcion, color):
        self.titulo = titulo
        self.descripcion = descripcion
        self.color = color


class CategoriaProtocolo(enum.Enum):
    system = "system"
    user = "user"
    arena = "arena"


class CodigoProtocolo(enum.Enum):
    sys_root = (
        "SYS_ROOT",
        "Acceso total al núcleo. Permite la reconfiguración de constantes globales del sistema.",
    )
    sys_purge = (
        "SYS_PURGE",
        "Protocolo de borrado definitivo. Capacidad para eliminar nodos, registros y sujetos permanentemente.",
    )
    usr_rewrite = (
        "USR_REWRITE",
        "Alteración de perfiles neurales. Permite modificar rangos, reputación y datos de identidad.",
    )
    usr_ban = (
        "USR_BAN",
        "Corte forzado de enlace. Expulsa y bloquea el acceso de cualquier sujeto al mainframe.",
    )
    arn_build = (
        "ARN_BUILD",
        "Creación de nodos de combate. Permite desplegar y gestionar torneos y eventos en vivo.",
    )
    arn_broadcast = (
        "ARN_BROADCAST",
        "Emisión de prioridad absoluta. Envía mensajes y alertas que sobrepasan cualquier interfaz de usuario.",
    )

    def __init__(self, codigo, capacidad):
        self.codigo = codigo
        self.capacidad = capacidad
