from flask import session, redirect, url_for, flash
from functools import wraps
import json
import os

DB_FILE = 'database.json'


# =========================
# READ DATABASE
# =========================
def read_db():

    if not os.path.exists(DB_FILE):

        return {
            "users": [],
            "mata_kuliah": [],
            "mahasiswa": [],
            "dosen_data": []
        }

    with open(DB_FILE, 'r') as f:
        return json.load(f)


# =========================
# WRITE DATABASE
# =========================
def write_db(data):

    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)


# =========================
# LOGIN REQUIRED
# =========================
def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):

        if 'logged_in' not in session:

            flash('Silakan login terlebih dahulu', 'error')

            return redirect(url_for('auth.login'))

        return f(*args, **kwargs)

    return decorated_function


# =========================
# ROLE REQUIRED
# =========================
def role_required(role):

    def decorator(f):

        @wraps(f)
        def decorated_function(*args, **kwargs):

            if session.get('role') != role:

                flash('Akses ditolak', 'error')

                return redirect(url_for('auth.login'))

            return f(*args, **kwargs)

        return decorated_function

    return decorator