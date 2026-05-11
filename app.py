from flask import Flask, redirect, url_for
import json
import os
import secrets
import hashlib

from blueprints.auth import auth_bp
from blueprints.mataKuliah import matakuliah_bp
from blueprints.mahasiswa import mahasiswa_bp
from blueprints.dosen import dosen_bp
from blueprints.users import users_bp

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

DB_FILE = 'database.json'

app.register_blueprint(auth_bp)
app.register_blueprint(matakuliah_bp)
app.register_blueprint(mahasiswa_bp)
app.register_blueprint(dosen_bp)
app.register_blueprint(users_bp)


def init_db():
    if not os.path.exists(DB_FILE):
        superadmin = {
            "id": 1,
            "username": "superadmin",
            "password": hashlib.sha256("superadmin123".encode()).hexdigest(),
            "role": "superadmin",
            "protected": True
        }
        dosen = {
            "id": 2,
            "username": "dosen",
            "password": hashlib.sha256("dosen123".encode()).hexdigest(),
            "role": "dosen",
            "protected": False
        }
        with open(DB_FILE, 'w') as f:
            json.dump({
                "users": [superadmin, dosen],
                "mata_kuliah": [],
                "mahasiswa": [],
                "dosen_data": []
            }, f, indent=4)

@app.route('/')
def home():
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)