from flask import Blueprint, render_template

rol_bp = Blueprint('roles', __name__, url_prefix='/roles')

@rol_bp.route('/')
def index():
    return render_template("dashboard/index.html")