from flask import Blueprint, request, render_template

from app.services import protocolos_services, dashboard_service

protocolo_bp = Blueprint("protocolo", __name__, url_prefix="/protocolos")

@protocolo_bp.route("",strict_slashes=False)
@protocolo_bp.route("/",strict_slashes=False)
def index():
    protocolos = protocolos_services.get_all_protocols()
    
    context = dashboard_service.get_dashboard_data(request.path)
    
    return render_template("dashboard/protocolos.html", protocolos=protocolos, **context)