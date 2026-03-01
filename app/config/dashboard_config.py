# --- CONSTANTES DE CONFIGURACIÓN DEL DASHBOARD ---
# Este archivo centraliza todos los datos estáticos que definen la apariencia
# y el contenido del panel de control.

METRIC_CARDS = [
    {
        "label": "NEURAL_SUBJECTS",
        "value": "5",
        "trend": "+12",
        "icon": "person",
        "color_class": "primary",
    },
    {
        "label": "TACTICAL_UNITS",
        "value": "128",
        "trend": "+2",
        "icon": "shield_person",
        "color_class": "secondary",
    },
    {
        "label": "ACTIVE_SQUADS",
        "value": "32",
        "trend": "-2",
        "icon": "groups",
        "color_class": "accent-yellow",
    },
    {
        "label": "ARENA_NODES",
        "value": "6",
        "trend": "+0.1%",
        "icon": "stadium",
        "color_class": "accent-blue",
    },
    {
        "label": "VIRTUAL_SOFTWARE",
        "value": "8",
        "trend": "+1",
        "icon": "sports_esports",
        "color_class": "primary",
    },
]

MENU_TITLES = [
    {"name_section": "OPERATIONS_COMMAND"},
    {"name_section": "ARENA_INFRASTRUCTURE"},
    {"name_section": "SYSTEM_KERNEL"},
    {"name_section": "DATA_TELEMETRY"},
]

MENU_ITEMS = [
    # --- SECCIÓN: OPERATIONS_COMMAND ---
    {
        "icon_main": "dashboard",
        "name_main": "MAINFRAME_HUB",
        "title_section": MENU_TITLES[0]["name_section"],
        "url": "/",
        "name_breadcrumbs": "NEXUS_OVERWATCH",
        "min_level": 80,
    },
    {
        "icon_main": "group",
        "name_main": "SUBJECT_PROFILES",
        "title_section": MENU_TITLES[0]["name_section"],
        "url": "/usuarios",
        "name_breadcrumbs": "FIRMAS_NEURALES",
        "min_level": 5,
    },
    {
        "icon_main": "shield_person",
        "name_main": "TACTICAL_SQUADS",
        "title_section": MENU_TITLES[0]["name_section"],
        "url": "/equipos",
        "name_breadcrumbs": "ESCUADRONES",
        "min_level": 5,
    },
    # --- SECCIÓN: ARENA_INFRASTRUCTURE ---
    {
        "icon_main": "emoji_events",
        "name_main": "ARENA_OPS",
        "title_section": MENU_TITLES[1]["name_section"],
        "url": "/torneos",
        "name_breadcrumbs": "INSTANCIAS",
        "min_level": 0,
    },
    {
        "icon_main": "videogame_asset",
        "name_main": "VIRTUAL_SOFTWARE",
        "title_section": MENU_TITLES[1]["name_section"],
        "url": "/juegos",
        "name_breadcrumbs": "SOFTWARE_VIRTUAL",
        "min_level": 0,
    },
    # --- SECCIÓN: SYSTEM_KERNEL ---
    {
        "icon_main": "verified_user",
        "name_main": "CLEARANCE_LVLS",
        "title_section": MENU_TITLES[2]["name_section"],
        "url": "/jerarquias",
        "name_breadcrumbs": "Niveles_Acceso",
        "min_level": 80,
    },
    {
        "icon_main": "settings_input_component",
        "name_main": "CORE_PROTOCOLS",
        "title_section": MENU_TITLES[2]["name_section"],
        "url": "/protocolos",
        "name_breadcrumbs": "REGLAS_BASE",
        "min_level": 80,
    },
    {
        "icon_main": "genetics",
        "name_main": "NEURAL_ARCHETYPES",
        "title_section": MENU_TITLES[2]["name_section"],
        "url": "/roles",
        "name_breadcrumbs": "Roles_de_combate",
        "min_level": 80,
    },
    # --- SECCIÓN: DATA_TELEMETRY ---
    {
        "icon_main": "receipt_long",
        "name_main": "REGISTER_ACTION",
        "title_section": "DATA_TELEMETRY",
        "url": "/registros",
        "name_breadcrumbs": "BITÁCORAS",
        "min_level": 20,
    },
    {
        "icon_main": "monitoring",
        "name_main": "PERFORMANCE_DATA",
        "title_section": "DATA_TELEMETRY",
        "url": "/resultados",
        "name_breadcrumbs": "ANALYTICS",
        "min_level": 50,
    },
]

ALERTS_DATA = [
    {
        "icon": "fingerprint",
        "title": "[REGISTRO_DE_SUJETOS_ACTIVO]",
        "subtitle": "Indexando firmas neurales en la base de datos central... Acceso concedido.",
        "url_info": "/usuarios",
        "btn_info": "VINCULAR_SUJETO",
        "access": ["ADMIN", "MOD_SISTEMA", "MOD_TACTICO", "MOD_ARENA", "PARTICIPANTE"],
    },
    {
        "icon": "account_tree",
        "title": "[ARQUITECTURA_DE_SINCRO_ORDEN]",
        "subtitle": "Mapeo dinámico de capacidad neural y rangos de mando... Ajustando privilegios de acceso.",
        "url_info": "/jerarquias",
        "btn_info": "INYECTAR_NIVEL_ACCESO",
        "access": ["ADMIN", "MOD_SISTEMA"],
    },
    {
        "icon": "psychology",
        "title": "[LIBRERÍA_DE_ADN_OPERATIVO]",
        "subtitle": "Especializaciones de combate codificadas. Cargando modelos de comportamiento de arquetipo.",
        "url_info": "/roles",
        "btn_info": "INYECTAR_PERFIL",
        "access": ["ADMIN", "MOD_SISTEMA"],
    },
    {
        "icon": "terminal",
        "title": "[MATRIZ_PROTOCOLOS_EJECUCIÓN]",
        "subtitle": "Definición de reglas críticas y comandos de acceso al Núcleo... Verificando sintaxis del sistema.",
        "url_info": "/protocolos",
        "btn_info": "INYECTAR_COMANDO",
        "access": ["ADMIN"],
    },
    {
        "icon": "extension",
        "title": "[MOTORES_DE_SIMULACION_VIRTUAL]",
        "subtitle": "Instalando enclaves neurales de alta densidad. Motores de renderizado de Arena listos.",
        "url_info": "/juegos",
        "btn_info": "INYECTAR_MOTOR",
        "access": ["ADMIN", "MOD_ARENA"],
    },
    {
        "icon": "military_tech",
        "title": "[DESPLIEGUE_DE_OPERACIONES_DE_ARENA]",
        "subtitle": "Sincronizando simulaciones de combate global... Detectando brechas de competición activas.",
        "url_info": "/torneos",
        "btn_info": "ABRIR_OPERACIÓN",
        "access": ["ADMIN", "MOD_ARENA"],
    },
    {
        "icon": "groups_3",
        "title": "[COLECTIVOS_DE_GUERRA_TÁCTICA]",
        "subtitle": "Unificación de nodos de combate. Analizando letalidad grupal y sinergia de red local.",
        "url_info": "/equipos",
        "btn_info": "FORJAR_CLUSTER",
        "access": ["ADMIN", "MOD_TACTICO"],
    },
    {
        "icon": "History_Edu",
        "title": "[REGISTROS_DE_SINCRONIZACIÓN]",
        "subtitle": "INICIA TU SECUENCIA DE REGISTRO NEURAL. ELIGE TU MODO DE COMBATE E INYÉCTATE EN LA SIMULACIÓN...",
        "url_info": "/registros",
        "btn_info": "TRAZAR_SESIÓN",
        "access": ["ADMIN"],
    },
    {
        "icon": "monitoring",
        "title": "[TELEMETRÍA_Y_EXTRACCIÓN_DE_DATOS]",
        "subtitle": "Cuantificando rendimiento neural post-combate... Generando reportes de eficiencia técnica.",
        "url_info": "/resultados",
        "btn_info": "EXPORTAR_LOGS",
        "access": ["ADMIN"],
    },
]
