"""Servicio de dashboard.

Maneja la lógica de agregación de datos para el dashboard, incluyendo:
- Filtrado de menús según permisos del usuario
- Determinación de alertas activas
- Cálculo de niveles de acceso
- Identificación de página activa y títulos de página
"""

from typing import Optional, Dict, List, Any, Tuple
from flask import current_app
from flask_login import current_user
from itertools import groupby
from operator import itemgetter

from app.utils.permissions import Permissions
from app.config import dashboard_config as config

# --- CONSTANTES ---
DEFAULT_PAGE_TITLE = "MAINFRAME_HUB"
DEFAULT_PAGE_DATA = "COMMAND_CENTER"
DEFAULT_MIN_ACCESS_LEVEL = Permissions.MOD_SISTEMA


# --- FUNCIONES AUXILIARES (HELPERS) ---


def _normalize_path(path: str) -> str:
    """Normaliza una ruta eliminando barras finales para comparaciones consistentes.

    Args:
        path (str): Ruta a normalizar (ej: "/roles/", "/equipos").

    Returns:
        str: Ruta normalizada (ej: "/roles", "/equipos", "/").

    Example:
        >>> _normalize_path("/roles/")
        '/roles'
        >>> _normalize_path("/")
        '/'
    """
    if not isinstance(path, str):
        current_app.logger.warning(f"_normalize_path recibió tipo inválido: {type(path)}")
        return "/"
    return path.rstrip("/") if len(path) > 1 else path


def _get_filtered_menu(user_level: int) -> List[Dict[str, Any]]:
    """Filtra los ítems del menú según el nivel de acceso del usuario.

    Args:
        user_level (int): Nivel de acceso del usuario (0-100).

    Returns:
        List[Dict]: Lista de ítems del menú accesibles para el usuario.

    Raises:
        TypeError: Si user_level no es un entero.
    """
    if not isinstance(user_level, int):
        raise TypeError(f"user_level debe ser int, recibido {type(user_level)}")

    return [
        item.copy()
        for item in config.MENU_ITEMS
        if user_level >= item.get("min_level", 0)
    ]


def _group_menu_by_section(filtered_menu_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Agrupa ítems del menú por su sección (title_section).

    Args:
        filtered_menu_items (List[Dict]): Ítems del menú ya filtrados.

    Returns:
        List[Dict]: Lista de secciones con sus ítems agrupados.
                    Estructura: [{"title": "SECTION_NAME", "section_items": [...]}, ...]

    Example:
        >>> items = [
        ...     {"title_section": "OPS", "name_main": "MENU1"},
        ...     {"title_section": "OPS", "name_main": "MENU2"},
        ... ]
        >>> _group_menu_by_section(items)
        [{"title": "OPS", "section_items": [...]}]
    """
    grouped_menu = []
    try:
        for key, group in groupby(filtered_menu_items, key=itemgetter("title_section")):
            grouped_menu.append({"title": key, "section_items": list(group)})
    except KeyError as e:
        current_app.logger.exception(f"Error agrupando menú: falta clave {e}")
        return []

    return grouped_menu


def _get_active_alert(normalized_path: str) -> Optional[Dict[str, Any]]:
    """Busca la alerta correspondiente a la ruta actual.

    Args:
        normalized_path (str): Ruta normalizada (sin barra final).

    Returns:
        Optional[Dict]: Diccionario de alerta si existe, None en caso contrario.
    """
    if not isinstance(normalized_path, str):
        current_app.logger.warning(f"_get_active_alert recibió tipo inválido: {type(normalized_path)}")
        return None

    try:
        return next(
            (
                alert
                for alert in config.ALERTS_DATA
                if _normalize_path(alert.get("url_info", "")) == normalized_path
            ),
            None,
        )
    except (KeyError, TypeError) as e:
        current_app.logger.exception(f"Error obteniendo alerta activa: {e}")
        return None


def _calculate_access_level(user: Any) -> int:
    """Calcula el nivel de permiso discreto basado en la jerarquía del usuario.

    Determina el nivel de acceso más alto aplicable al usuario, evaluando
    de mayor a menor permiso (ADMIN > MOD_SISTEMA > MOD_ARENA > MOD_TACTICO > PARTICIPANTE).

    Args:
        user (Any): Objeto usuario autenticado (con atributo jerarquia).

    Returns:
        int: Nivel de permiso (0-100).
    """
    # Si no está autenticado, retorna nivel básico
    if not user.is_authenticated:
        return Permissions.PARTICIPANTE

    try:
        level = user.jerarquia.nivel_acceso
    except (AttributeError, TypeError) as e:
        current_app.logger.exception(f"Error accediendo jerarquía de usuario: {e}")
        return Permissions.PARTICIPANTE

    # Evaluamos de mayor a menor para encontrar el permiso más alto aplicable
    if level >= Permissions.ADMIN:
        return Permissions.ADMIN
    if level >= Permissions.MOD_SISTEMA:
        return Permissions.MOD_SISTEMA
    if level >= Permissions.MOD_ARENA:
        return Permissions.MOD_ARENA
    if level >= Permissions.MOD_TACTICO:
        return Permissions.MOD_TACTICO

    return Permissions.PARTICIPANTE


def _mark_active_menu_and_get_page_info(
    grouped_menu_data: List[Dict[str, Any]], current_path: str
) -> Tuple[str, str]:
    """Marca los ítems activos en el menú y retorna info de página.

    Itera sobre el menú agrupado, comparando URLs normalizadas con la ruta actual.
    Marca como activo el primer ítem que coincida y retorna su información.

    Args:
        grouped_menu_data (List[Dict]): Menú agrupado por secciones.
        current_path (str): Ruta actual (ya normalizada).

    Returns:
        Tuple[str, str]: (page_title, page_data) del ítem activo o valores por defecto.
    """
    page_title = DEFAULT_PAGE_TITLE
    page_data = DEFAULT_PAGE_DATA

    for section in grouped_menu_data:
        section_items = section.get("section_items", [])
        for item in section_items:
            norm_item_url = _normalize_path(item.get("url", "#"))

            if norm_item_url == current_path:
                item["active"] = True
                page_title = item.get("name_main", DEFAULT_PAGE_TITLE)
                page_data = item.get("name_breadcrumbs", DEFAULT_PAGE_DATA)
                current_app.logger.debug(f"Ítem activo: {page_title}")
                return page_title, page_data
            else:
                item["active"] = False

    current_app.logger.debug(f"No se encontró ítem activo para ruta: {current_path}")
    return page_title, page_data


# --- FUNCIÓN PRINCIPAL ---


def get_dashboard_data(current_path: str) -> Dict[str, Any]:
    """Retorna configuración completa del dashboard para la ruta actual.

    Agrega datos de menú, alertas, métricas y permisos según:
    - Nivel de acceso del usuario autenticado
    - Ruta HTTP actual
    - Configuración centralizada (dashboard_config)

    Args:
        current_path (str): Ruta HTTP actual (ej: "/roles", "/equipos/").

    Returns:
        Dict[str, Any]: Diccionario con claves:
            - metric_cards: Lista de tarjetas de métricas.
            - menu_data: Menú agrupado por secciones (con activo marcado).
            - alerts_data: Todas las alertas disponibles.
            - alert_finish: Alerta para la ruta actual (o None).
            - page_data: Nombre de breadcrumb de la página activa.
            - page_title: Título de la página activa.
            - access_value: Nivel de permiso del usuario.
            - min_access_level: Nivel mínimo requerido para vistas protegidas.

    Raises:
        TypeError: Si current_path no es un string válido.

    Example:
        >>> data = get_dashboard_data("/roles")
        >>> data['page_title']
        'ROLES_MANAGEMENT'
        >>> data['access_value']
        80
    """
    # Validar entrada
    if not isinstance(current_path, str):
        raise TypeError(f"current_path debe ser str, recibido {type(current_path)}")

    if not current_path:
        current_app.logger.warning("current_path vacío, usando '/'")
        current_path = "/"

    # 1. Normalizar ruta actual
    norm_path = _normalize_path(current_path)

    # 2. Obtener y filtrar menú según usuario
    grouped_menu_data: List[Dict[str, Any]] = []
    access_value = Permissions.PARTICIPANTE

    if current_user.is_authenticated:
        try:
            user_level = current_user.jerarquia.nivel_acceso
            filtered_items = _get_filtered_menu(user_level)
            grouped_menu_data = _group_menu_by_section(filtered_items)
            access_value = _calculate_access_level(current_user)
            current_app.logger.debug(
                f"Menú generado para usuario {current_user.id_usuario}: {len(filtered_items)} ítems"
            )
        except Exception as e:
            current_app.logger.exception(f"Error generando menú para usuario: {e}")
            grouped_menu_data = []

    # 3. Determinar alerta activa
    alert_finish = _get_active_alert(norm_path)

    # 4. Marcar items activos y obtener info de página
    page_title, page_data = _mark_active_menu_and_get_page_info(grouped_menu_data, norm_path)

    # 5. Construir y retornar contexto
    context = {
        "metric_cards": config.METRIC_CARDS,
        "menu_data": grouped_menu_data,
        "alerts_data": config.ALERTS_DATA,
        "alert_finish": alert_finish,
        "page_data": page_data,
        "page_title": page_title,
        "access_value": access_value,
        "min_access_level": DEFAULT_MIN_ACCESS_LEVEL,
    }

    current_app.logger.debug(
        f"Dashboard data generado para ruta {norm_path}: "
        f"access_value={access_value}, alert={alert_finish is not None}"
    )
    return context
