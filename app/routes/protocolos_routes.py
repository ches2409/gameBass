from flask import Blueprint, request, render_template, redirect, url_for

from app.enums.tipos import CodigoProtocolo, CategoriaProtocolo
from app.services import protocolos_services, dashboard_service

protocolo_bp = Blueprint("protocolo", __name__, url_prefix="/protocolos")

@protocolo_bp.route("",strict_slashes=False)
@protocolo_bp.route("/",strict_slashes=False)
def index():
    protocolos = protocolos_services.get_all_protocols()
    
    context = dashboard_service.get_dashboard_data(request.path)
    
    # CORRECCIÓN: Usamos 'codigos_listado' y 'categorias_listado' para coincidir con el HTML
    return render_template("dashboard/protocolos.html", protocolos=protocolos, codigos_listado=CodigoProtocolo, categorias_listado=CategoriaProtocolo ,**context)

@protocolo_bp.route("/create", methods=['GET', 'POST'] , strict_slashes=False)
def create():
    if request.method == 'POST':
        codigo_protocolo_txt = request.form.get('codigo_de_protocolo')
        nombre_protocolo = request.form['nombre_de_protocolo']
        categoria_protocolo_txt = request.form.get('categoria_de_protocolo')
        descripcion_protocolo = request.form.get('descripcion_de_protocolo')
        
        codigo_protocolo = next((e for e in CodigoProtocolo if e.codigo == codigo_protocolo_txt), None)
        categoria_protocolo = next(e for e in CodigoProtocolo if e.capacidad == categoria_protocolo_txt)
        
        if protocolos_services.create_protocol(codigo_protocolo, nombre_protocolo, categoria_protocolo):
            return redirect(url_for('protocolo.index'))
        
    return render_template("dashboard/protocolos/create.html", codigos_listado=CodigoProtocolo, categorias_listado=CategoriaProtocolo)
    