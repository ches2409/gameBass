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
        {'name_section': 'ESTRATEGIA_MAESTRA'},
        {'name_section': 'INFRAESTRUCTURA_CONTIENDA'},
        {'name_section': 'SEGURIDAD_Y_NUCLEO'},
        {'name_section':'security_node'},
        {'name_section':'neural_network'},
        
    ]
    
    menu_data = [
        {'icon_main': 'dashboard', 'name_main': 'MAINFRAME_HUB', 'title_section': menu_titles[0]['name_section'], 'url': '/','name_breadcrumbs':'NEXUS_OVERWATCH'},
        {'icon_main': 'group', 'name_main': 'NEURAL_PROFILES', 'title_section': menu_titles[0]['name_section'], 'url': '/usuarios','name_breadcrumbs':'GHOST_ARCHIVES'},
        {'icon_main': 'shield_person', 'name_main': 'TACTICAL_SQUADS', 'title_section': menu_titles[0]['name_section'], 'url': '/equipos','name_breadcrumbs':'SYNERGY_CORES'},
        {'icon_main': 'emoji_events', 'name_main': 'ARENA_OPS', 'title_section': menu_titles[1]['name_section'], 'url': '/arena','name_breadcrumbs':'CONFLICT_THEATERS'},
        {'icon_main': 'sports_esports', 'name_main': 'VIRTUAL_SOFTWARE','title_section': menu_titles[1]['name_section'], 'url': '/software','name_breadcrumbs':'DIGITAL_FABRIC'},
        {'icon_main': 'verified_user', 'name_main': 'CLEARANCE_LVLS', 'title_section': menu_titles[2]['name_section'], 'url': '/jerarquias','name_breadcrumbs':'ASCENSION_STRATA'},
        {'icon_main': 'settings_input_component', 'name_main': 'CORE_PROTOCOLS','title_section': menu_titles[2]['name_section'], 'url': '/protocolos','name_breadcrumbs':'NEURAL_CORE'},
        {'icon_main': 'genetics', 'name_main': 'NEURAL_ARCHETYPES', 'title_section': menu_titles[2]['name_section'], 'url': '/roles', 'name_breadcrumbs': 'PRIME_ETHOS'}
        
    ]

    # 3. Datos de Alertas
    alerts_data = [
        {'icon': 'frame_person', 'title': '[INYECCION_SUJETO_DETECTADA]','subtitle': 'Monitoreando nuevos enlaces neurales en el Sector_Omega...', 'url_info': '/usuarios', 'btn_info':'INYECTAR_SUJETO'},
        {'icon': 'hub', 'title': '[ARQUITECTURA_DE_SINCRO_ORDEN]','subtitle': 'Mapeo dinámico de capacidad nerual y autoridad de mando...', 'url_info': '/jerarquias','btn_info':'INYECTAR_NIVEL_ACCESO'},
        {'icon': 'biotech', 'title': '[LIBRERÍA_DE_ADN_OPERATIVO]','subtitle': 'Gestión de arquetipos y modelos neurales...', 'url_info': '/roles', 'btn_info':'INYECTAR_ROL'},
        {'icon': 'terminal', 'title': '[MATRIZ_PROTOCOLOS_EJECUCIÓN]', 'subtitle': 'Definición de reglas de acceso al nucleo...', 'url_info': '/protocolos', 'btn_info': 'INYECTAR_NODO'},
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