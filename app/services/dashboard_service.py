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
        {'label': 'ARENA_NODES', 'value': '99.8%', 'trend': '+0.1%', 'icon': 'stadium', 'color_class': 'accent-blue'}
    ]

    # 2. Datos del Menú Lateral
    menu_titles = [
        {'name_section': 'ESTRATEGIA_MAESTRA'},
        {'name_section': 'INFRAESTRUCTURA_CONTIENDA'},
        {'name_section': 'SEGURIDAD_Y_NUCLEO'},
    ]
    
    menu_data = [
        {'icon_main': 'dashboard', 'name_main': 'MAINFRAME_HUB', 'title_section': menu_titles[0]['name_section']},
        {'icon_main': 'group', 'name_main': 'NEURAL_PROFILES', 'title_section': menu_titles[0]['name_section']},
        {'icon_main': 'shield_person', 'name_main': 'TACTICAL_SQUADS', 'title_section': menu_titles[0]['name_section']},
        {'icon_main': 'emoji_events', 'name_main': 'ARENA_OPS', 'title_section': menu_titles[1]['name_section']},
        {'icon_main': 'sports_esports', 'name_main': 'VIRTUAL_SOFTWARE','title_section': menu_titles[1]['name_section']},
        {'icon_main': 'verified_user', 'name_main': 'CLEARANCE_LVLS', 'title_section': menu_titles[2]['name_section']},
        {'icon_main': 'settings_input_component', 'name_main': 'CORE_PROTOCOLS','title_section': menu_titles[2]['name_section']}
    ]

    # 3. Datos de Alertas
    alerts_data = [
        {'icon': 'sensors', 'title': '[INYECCION_SUJETO_DETECTADA]','subtitle': 'Monitoreando nuevos enlaces neurales en el Sector_Omega...', 'url_info': '/'},
        {'icon': 'group', 'title': '[EQUIPOS]','subtitle': 'Monitoreando nuevos TACTICAS...', 'url_info': '/roles'}
    ]

    # 4. Lógica para encontrar la alerta activa
    alert_finish = None
    for alert in alerts_data:
        # Normalizamos las rutas quitando barras finales para comparar '/roles' con '/roles/'
        if alert['url_info'].rstrip('/') == current_path.rstrip('/'):
            alert_finish = alert
            break

    return {
        'metric_cards': metric_cards,
        'menu_titles': menu_titles,
        'menu_data': menu_data,
        'alerts_data': alerts_data,
        'alert_finish': alert_finish
    }