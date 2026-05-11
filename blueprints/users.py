from flask import Blueprint, render_template
from blueprints.utils import read_db, login_required, role_required

users_bp = Blueprint('users', __name__, url_prefix='/users')


@users_bp.route('/')
@login_required
@role_required('superadmin')
def index():
    data = read_db()
    return render_template('users.html', users=data['users'])