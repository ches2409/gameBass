from flask import Blueprint, request, render_template

from app.services import jerarquias_services, dashboard_service

jerarquia_bp=Blueprint("jerarquia",__name__,url_prefix="/jerarquias")

@jerarquia_bp.route("", strict_slashes=False)
@jerarquia_bp.route("/", strict_slashes=False)
def index():
    
    try:
        jerarquias = jerarquias_services.get_all_jerarquias()
    except Exception as e:
        print(f"Error al obtener jerarquias {e}")
        
        jerarquias =[]
        
    context = dashboard_service.get_dashboard_data(request.path)
    
    return render_template('dashboard/jerarquias.html', jerarquias=jerarquias, **context)
