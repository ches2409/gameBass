from flask import Blueprint, render_template

inicio_bp = Blueprint('index', __name__)

@inicio_bp.route('/')
@inicio_bp.route('/<indice>')
def inicio(indice=1):
    return render_template("dashboard/index.html")
