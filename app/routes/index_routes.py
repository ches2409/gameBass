from flask import Blueprint, render_template, request
from app.services import dashboard_service

inicio_bp = Blueprint('index', __name__)

@inicio_bp.route('/',strict_slashes=False)
def index():
    # Obtenemos toda la data visual desde el servicio
    context = dashboard_service.get_dashboard_data(request.path)
    
    # Pasamos el contexto desempaquetado (**context) a la plantilla
    return render_template("dashboard/index.html", **context)
