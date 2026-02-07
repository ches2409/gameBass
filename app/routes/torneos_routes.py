from flask import Blueprint, request, render_template

from app.services import dashboard_service, torneos_services

torneos_bp = Blueprint('torneo', __name__, url_prefix='/torneos')

@torneos_bp.route('/')
def index():
    
    context=dashboard_service.get_dashboard_data(request.path)
    
    torneos_list=torneos_services.get_all_torneos()
    
    return render_template(
        'dashboard/torneos.html',
        torneos_list=torneos_list,
        **context
    )