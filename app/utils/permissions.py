"""Sistema de control de permisos jerárquico para GameBass.

Define cinco niveles de acceso con un modelo jerárquico donde cada nivel
superior hereda permisos de los inferiores. Los permisos se expresan como
valores numéricos (0-100) y se agrupan en perfiles para facilitar su uso
en decoradores de rutas y validaciones de acceso.

Niveles (de mayor a menor privilerio):
  - ADMIN (100): Control total del sistema.
  - MOD_SISTEMA (80): Gestión de usuarios, torneos y configuración global.
  - MOD_ARENA (60): Gestión de torneos, juegos, resultados.
  - MOD_TACTICO (40): Gestión de equipos, participaciones.
  - PARTICIPANTE (0): Acceso básico sin administración.

Ejemplo de uso:
  >>> from app.utils.permissions import Permissions, Profiles
  >>> Permissions.get_name(100)
  'ADMIN'
  >>> Permissions.is_valid(80)
  True
  >>> len(Profiles.SISTEMA)  # Permisos agrupados para validators
  2

"""

from typing import Dict, List, Optional


class Permissions:
    """Definición de niveles de permisos como constantes numéricas.

    Cada nivel representa un rango de privilegios. El número indica
    la jerarquía: valores mayores = privilegios superiores.
    """

    # Configuración total del sistema
    ADMIN: int = 90

    # Gestión de Usuarios, Torneos y Configuración Global
    MOD_SISTEMA: int = 80

    # Gestión de Torneos, Juegos, Resultados y Validaciones
    MOD_ARENA: int = 60

    # Gestión de Equipos y Participaciones Tácticas
    MOD_TACTICO: int = 40

    # Participante, acceso a juegos(ver) y torneos(ver), registrarse
    PARTICIPANTE: int = 20

    # Usuario visitante(en espera de aceptacion), solo puede ver torneos, juego y perfil de usuario
    VISITANTE: int = 5

    # --- Caché interna para búsquedas inversas ---
    _NAME_CACHE: Optional[Dict[int, str]] = None

    @classmethod
    def _build_cache(cls) -> Dict[int, str]:
        """Construye un diccionario interno: valor -> nombre.

        Se ejecuta una sola vez para mejorar el rendimiento de búsquedas.

        Returns:
            Dict[int, str]: Mapeo {valor_numerico: nombre_string}
        """
        if cls._NAME_CACHE is not None:
            return cls._NAME_CACHE

        cls._NAME_CACHE = {}
        for key, val in vars(cls).items():
            if not key.startswith("_") and isinstance(val, int):
                cls._NAME_CACHE[val] = key

        return cls._NAME_CACHE

    @classmethod
    def get_name(cls, value: int) -> str:
        """Retorna el nombre del nivel de permiso basado en su valor.

        Args:
            value (int): Valor numérico del permiso (0-100).

        Returns:
            str: Nombre del nivel (ej: 'ADMIN') o 'UNKNOWN' si no existe.

        Example:
            >>> Permissions.get_name(100)
            'ADMIN'
            >>> Permissions.get_name(999)
            'UNKNOWN'
        """
        if value >= cls.ADMIN:
            return "ADMIN"

        cache = cls._build_cache()
        return cache.get(value, "UNKNOWN")

    @classmethod
    def is_valid(cls, value: int) -> bool:
        """Verifica si un valor es un nivel de permiso válido.

        Args:
            value (int): Valor a validar.

        Returns:
            bool: True si el valor está en el conjunto de permisos definidos.

        Example:
            >>> Permissions.is_valid(80)
            True
            >>> Permissions.is_valid(999)
            False
        """
        cache = cls._build_cache()
        return value in cache

    @classmethod
    def get_levels_gte(cls, min_level: int) -> List[int]:
        """Retorna todos los niveles mayores o iguales al especificado.

        Útil para validar acceso: si un usuario tiene nivel >= MOD_ARENA,
        puede acceder a recursos de MOD_ARENA y superiores.

        Args:
            min_level (int): Nivel mínimo requerido.

        Returns:
            List[int]: Niveles que cumplen con el criterio, ordenados
                       de mayor a menor.

        Example:
            >>> Permissions.get_levels_gte(60)
            [100, 80, 60]
        """
        cache = cls._build_cache()
        return sorted([v for v in cache.keys() if v >= min_level], reverse=True)

    @classmethod
    def profiles(cls) -> List[Dict[str, object]]:
        """Retorna lista de perfiles para poblar selectores en la UI.

        Se usa en formularios de asignación de roles y permisos.

        Returns:
            List[Dict]: Cada dict contiene 'name', 'value', 'label'.

        Example:
            >>> p = Permissions.profiles()
            >>> p[0]['label']
            'ADMINISTRADOR (Nivel 100)'
        """
        return [
            {
                "name": "ADMIN",
                "value": cls.ADMIN,
                "label": "ADMINISTRADOR (Nivel 90)",
            },
            {
                "name": "MOD_SISTEMA",
                "value": cls.MOD_SISTEMA,
                "label": "MODERADOR SISTEMA (Nivel 80)",
            },
            {
                "name": "MOD_ARENA",
                "value": cls.MOD_ARENA,
                "label": "MODERADOR ARENA (Nivel 60)",
            },
            {
                "name": "MOD_TACTICO",
                "value": cls.MOD_TACTICO,
                "label": "MODERADOR TÁCTICO (Nivel 40)",
            },
            {
                "name": "PARTICIPANTE",
                "value": cls.PARTICIPANTE,
                "label": "PARTICIPANTE (Nivel 20)",
            },
            {
                "name": "VISITANTE",
                "value": cls.VISITANTE,
                "label": "VISITANTE (Nivel 5)",
            },
        ]


class Profiles:
    """Agrupaciones de permisos para usar en decoradores y validadores.

    Cada atributo es una lista de niveles de permiso que otorgan acceso
    a una funcionalidad protegida. Se usa con @permission_required(*Profiles.ARENA).

    Ejemplo:
        @app.route('/admin')
        @permission_required(*Profiles.ROOT)
        def admin_panel():
            return "Acceso restringido a ADMIN"
    """

    # Sólo nivel ADMIN
    ROOT: List[int] = [Permissions.ADMIN]

    # ADMIN + MOD_SISTEMA
    SISTEMA: List[int] = [Permissions.ADMIN, Permissions.MOD_SISTEMA]

    # ADMIN + MOD_ARENA
    ARENA: List[int] = [Permissions.ADMIN, Permissions.MOD_ARENA]

    # ADMIN + MOD_TACTICO
    TACTICO: List[int] = [Permissions.ADMIN, Permissions.MOD_TACTICO]

    # ADMIN + PARTICIPANTE
    PARTICIPANTE: List[int] = [Permissions.ADMIN, Permissions.PARTICIPANTE]

    # ADMIN + VISITANTE
    VISITANTE: List[int] = [Permissions.VISITANTE]

    # Todos los permisos (para testing u operaciones globales)
    ALL: List[int] = [
        Permissions.ADMIN,
        Permissions.MOD_SISTEMA,
        Permissions.MOD_ARENA,
        Permissions.MOD_TACTICO,
        Permissions.PARTICIPANTE,
        Permissions.VISITANTE,
    ]
