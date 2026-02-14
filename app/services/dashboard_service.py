def get_dashboard_data(current_path):
    """
    Retorna un diccionario con toda la configuración visual del dashboard
    (Menús, Métricas, Alertas) y calcula la alerta activa según la URL.
    """

    # 1. Datos de Métricas (Header)
    metric_cards = [
        {'label': 'NEURAL_SUBJECTS', 'value': '5', 'trend': '+12', 'icon': 'person', 'color_class': 'primary'},
        {'label': 'TACTICAL_UNITS', 'value': '128', 'trend': '+2', 'icon': 'shield_person', 'color_class': 'secondary'},
        {'label': 'ACTIVE_SQUADS', 'value': '32', 'trend': '-2', 'icon': 'groups', 'color_class': 'accent-yellow'},
        {'label': 'ARENA_NODES', 'value': '6', 'trend': '+0.1%', 'icon': 'stadium', 'color_class': 'accent-blue'},
        {'label': 'VIRTUAL_SOFTWARE', 'value': '8', 'trend': '+1', 'icon': 'sports_esports', 'color_class': 'primary'}
    ]

    # 2. Datos del Menú Lateral
    menu_titles = [
        {"name_section": "OPERATIONS_COMMAND"},
        {"name_section": "ARENA_INFRASTRUCTURE"},
        {"name_section": "SYSTEM_KERNEL"},
        {"name_section": "DATA_TELEMETRY"},
    ]

    menu_data = [
        # --- SECCIÓN: OPERATIONS_COMMAND ---
        {
            "icon_main": "dashboard",
            "name_main": "MAINFRAME_HUB",
            "title_section": menu_titles[0]["name_section"],
            "url": "/",
            "name_breadcrumbs": "NEXUS_OVERWATCH",
        },
        {
            "icon_main": "group",
            "name_main": "SUBJECT_PROFILES",
            "title_section": menu_titles[0]["name_section"],
            "url": "/usuarios",
            "name_breadcrumbs": "DATABASE_SUBJECTS",
        },
        {
            "icon_main": "shield_person",
            "name_main": "TACTICAL_SQUADS",
            "title_section": menu_titles[0]["name_section"],
            "url": "/equipos",
            "name_breadcrumbs": "SQUAD_ROSTER",
        },
        # --- SECCIÓN: ARENA_INFRASTRUCTURE ---
        {
            "icon_main": "emoji_events",
            "name_main": "ARENA_OPS",
            "title_section": menu_titles[1]["name_section"],
            "url": "/torneos",
            "name_breadcrumbs": "ACTIVE_TOURNAMENTS",
        },
        {
            "icon_main": "videogame_asset",
            "name_main": "VIRTUAL_SOFTWARE",
            "title_section": menu_titles[1]["name_section"],
            "url": "/juegos",
            "name_breadcrumbs": "VIRTUAL_SOFTWARE_ENGINE",
        },
        # --- SECCIÓN: SYSTEM_KERNEL ---
        {
            "icon_main": "verified_user",
            "name_main": "CLEARANCE_LVLS",
            "title_section": menu_titles[2]["name_section"],
            "url": "/jerarquias",
            "name_breadcrumbs": "SECURITY_CLEARANCE_PROTOCOL",
        },
        {
            "icon_main": "settings_input_component",
            "name_main": "CORE_PROTOCOLS",
            "title_section": menu_titles[2]["name_section"],
            "url": "/protocolos",
            "name_breadcrumbs": "SYSTEM_COMMAND_LOG",
        },
        {
            "icon_main": "genetics",
            "name_main": "NEURAL_ARCHETYPES",
            "title_section": menu_titles[2]["name_section"],
            "url": "/roles",
            "name_breadcrumbs": "ARCHETYPE_TEMPLATE_CATALOG",
        },
        # --- SECCIÓN: DATA_TELEMETRY ---
        {
            "icon_main": "receipt_long",  # Representa una lista de eventos/logs
            "name_main": "ACTION_LOGS",
            "title_section": "DATA_TELEMETRY",
            "url": "/registros",
            "name_breadcrumbs": "SINCRO_HISTORY_LOG",
        },
        {
            "icon_main": "monitoring",  # Representa análisis y gráficos de rendimiento
            "name_main": "PERFORMANCE_DATA",
            "title_section": "DATA_TELEMETRY",
            "url": "/resultados",
            "name_breadcrumbs": "NEURAL_YIELD_ANALYSIS",
        },
    ]

    # 3. Datos de Alertas
    alerts_data = [
        {
            "icon": "fingerprint",
            "title": "[REGISTRO_DE_SUJETOS_ACTIVO]",
            "subtitle": "Indexando firmas neurales en la base de datos central... Acceso concedido.",
            "url_info": "/usuarios",
            "btn_info": "VINCULAR_SUJETO",
        },
        {
            "icon": "account_tree",
            "title": "[ARQUITECTURA_DE_SINCRO_ORDEN]",
            "subtitle": "Mapeo dinámico de capacidad neural y rangos de mando... Ajustando privilegios de acceso.",
            "url_info": "/jerarquias",
            "btn_info": "INYECTAR_NIVEL_ACCESO",
        },
        {
            "icon": "psychology",
            "title": "[LIBRERÍA_DE_ADN_OPERATIVO]",
            "subtitle": "Especializaciones de combate codificadas. Cargando modelos de comportamiento de arquetipo.",
            "url_info": "/roles",
            "btn_info": "INYECTAR_PERFIL",
        },
        {
            "icon": "terminal",
            "title": "[MATRIZ_PROTOCOLOS_EJECUCIÓN]",
            "subtitle": "Definición de reglas críticas y comandos de acceso al Núcleo... Verificando sintaxis del sistema.",
            "url_info": "/protocolos",
            "btn_info": "INYECTAR_COMANDO",
        },
        {
            "icon": "extension",
            "title": "[MOTORES_DE_SIMULACION_VIRTUAL]",
            "subtitle": "Instalando enclaves neurales de alta densidad. Motores de renderizado de Arena listos.",
            "url_info": "/juegos",
            "btn_info": "INYECTAR_MOTOR",
        },
        {
            "icon": "military_tech",
            "title": "[DESPLIEGUE_DE_OPERACIONES_DE_ARENA]",
            "subtitle": "Sincronizando simulaciones de combate global... Detectando brechas de competición activas.",
            "url_info": "/torneos",
            "btn_info": "ABRIR_OPERACIÓN",
        },
        {
            "icon": "groups_3",
            "title": "[COLECTIVOS_DE_GUERRA_TÁCTICA]",
            "subtitle": "Unificación de nodos de combate. Analizando letalidad grupal y sinergia de red local.",
            "url_info": "/equipos",
            "btn_info": "FORJAR_CLUSTER",
        },
        {
            "icon": "History_Edu",  # Representa la "Caja Negra" o bitácora
            "title": "[REGISTROS_DE_SINCRONIZACIÓN]",
            "subtitle": "Extrayendo bitácoras de participación en la Arena... Reconstruyendo eventos de combate.",
            "url_info": "/registros",
            "btn_info": "TRAZAR_SESIÓN",
        },
        {
            "icon": "monitoring",  # Representa telemetría y gráficos
            "title": "[TELEMETRÍA_Y_EXTRACCIÓN_DE_DATOS]",
            "subtitle": "Cuantificando rendimiento neural post-combate... Generando reportes de eficiencia técnica.",
            "url_info": "/resultados",
            "btn_info": "EXPORTAR_LOGS",
        },
    ]

    # 4. Lógica para encontrar la alerta activa
    alert_finish = None
    for alert in alerts_data:
        # Normalizar las rutas quitando barras finales para comparar '/roles' con '/roles/'
        if alert['url_info'].rstrip('/') == current_path.rstrip('/'):
            alert_finish = alert
            break
    if current_path.rstrip('/') == '':
        route_path ='COMMAND_CENTER'
    else:
        route_path = current_path.rstrip('/').upper()

    # 5. Lógica para determinar el título de la página y el ítem activo del menú
    page_title = 'MAINFRAME_HUB' # Título por defecto
    page_data = 'COMMAND_CENTER' # Valor por defecto para el breadcrumb

    # Normalizar la ruta actual (si es '/' se queda igual, si no, quitamos slash final)
    norm_path = current_path.rstrip('/') if len(current_path) > 1 else current_path

    for item in menu_data:
        # Normalizar la ruta del ítem
        page_breadcrumbs= item['name_breadcrumbs']
        item_url = item.get('url', '#')
        norm_item_url = item_url.rstrip('/') if len(item_url) > 1 else item_url

        if norm_item_url == norm_path:
            item['active'] = True
            page_title = item['name_main']
            page_data = item['name_breadcrumbs']
        else:
            item['active'] = False

    return {
        'metric_cards': metric_cards,
        'menu_titles': menu_titles,
        'menu_data': menu_data,
        'alerts_data': alerts_data,
        'alert_finish': alert_finish,
        'page_data':page_data,
        'page_title': page_title
    }
