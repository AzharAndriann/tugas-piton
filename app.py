from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os
import secrets
import hashlib
from functools import wraps

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

DB_FILE = 'database.json'


# ======================================================
# LOGIN REQUIRED
# ======================================================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'token' not in session or not session.get('logged_in'):
            flash('Silakan login terlebih dahulu.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ======================================================
# ROLE REQUIRED
# ======================================================
def role_required(*roles):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get('role') not in roles:
                flash('Akses ditolak.', 'error')
                return redirect(url_for('matakuliah'))
            return f(*args, **kwargs)
        return decorated_function
    return wrapper


# ======================================================
# INIT DATABASE
# ======================================================
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


# ======================================================
# READ WRITE JSON
# ======================================================
def read_db():
    init_db()
    with open(DB_FILE, 'r') as f:
        return json.load(f)


def write_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)


# ======================================================
# FIND USER
# ======================================================
def find_user(username):
    data = read_db()

    for user in data['users']:
        if user['username'] == username:
            return user

    return None


# ======================================================
# LOGIN
# ======================================================
@app.route('/', methods=['GET', 'POST'])
def login():

    if session.get('logged_in'):
        return redirect(url_for('matakuliah'))

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        user = find_user(username)

        hashed = hashlib.sha256(password.encode()).hexdigest()

        if user and user['password'] == hashed:

            session['logged_in'] = True
            session['username'] = username
            session['role'] = user['role']
            session['token'] = secrets.token_urlsafe(32)

            flash('Login berhasil', 'success')

            return redirect(url_for('matakuliah'))

        else:
            flash('Username atau password salah', 'error')

    return render_template('login.html')


# ======================================================
# LOGOUT
# ======================================================
@app.route('/logout')
def logout():
    session.clear()
    flash('Berhasil logout', 'info')
    return redirect(url_for('login'))


# ======================================================
# MATA KULIAH
# ======================================================
@app.route('/matakuliah')
@login_required
def matakuliah():
    data = read_db()
    return render_template(
        'matakuliah/index.html',
        data_mk=data['mata_kuliah']
    )


@app.route('/matakuliah/tambah', methods=['GET', 'POST'])
@login_required
def tambah_matakuliah():

    if request.method == 'POST':

        data = read_db()

        data['mata_kuliah'].append({
            "kode_matkul": int(request.form['kode_matkul']),
            "nama_mk": request.form['nama_mk'],
            "fakultas": request.form['fakultas'],
            "sks": request.form['sks']
        })

        write_db(data)

        return redirect(url_for('matakuliah'))

    return render_template('matakuliah/add.html')


@app.route('/matakuliah/edit/<int:kode_matkul>', methods=['GET', 'POST'])
@login_required
def edit_matakuliah(kode_matkul):

    data = read_db()

    mk = next(
        (x for x in data['mata_kuliah']
         if x['kode_matkul'] == kode_matkul),
        None
    )

    if request.method == 'POST':

        mk['nama_mk'] = request.form['nama_mk']
        mk['fakultas'] = request.form['fakultas']
        mk['sks'] = request.form['sks']

        write_db(data)

        return redirect(url_for('matakuliah'))

    return render_template('matakuliah/edit.html', mk=mk)


@app.route('/matakuliah/delete/<int:kode_matkul>')
@login_required
def delete_matakuliah(kode_matkul):

    data = read_db()

    data['mata_kuliah'] = [
        x for x in data['mata_kuliah']
        if x['kode_matkul'] != kode_matkul
    ]

    write_db(data)

    return redirect(url_for('matakuliah'))


# ======================================================
# MAHASISWA
# ======================================================
@app.route('/mahasiswa')
@login_required
def mahasiswa():

    data = read_db()

    return render_template(
        'mahasiswa/index.html',
        mahasiswa=data['mahasiswa']
    )


@app.route('/mahasiswa/tambah', methods=['GET', 'POST'])
@login_required
@role_required('dosen')
def tambah_mahasiswa():

    if request.method == 'POST':

        data = read_db()

        mahasiswa = {
            "id": len(data['mahasiswa']) + 1,
            "nama": request.form['nama'],
            "npm": request.form['npm'],
            "no_telp": request.form['no_telp'],
            "role": request.form['role']
        }

        data['mahasiswa'].append(mahasiswa)

        write_db(data)

        return redirect(url_for('mahasiswa'))

    return render_template('mahasiswa/add.html')


@app.route('/mahasiswa/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('dosen')
def edit_mahasiswa(id):

    data = read_db()

    mahasiswa = next(
        (m for m in data['mahasiswa'] if m['id'] == id),
        None
    )

    if request.method == 'POST':

        mahasiswa['nama'] = request.form['nama']
        mahasiswa['npm'] = request.form['npm']
        mahasiswa['no_telp'] = request.form['no_telp']
        mahasiswa['role'] = request.form['role']

        write_db(data)

        return redirect(url_for('mahasiswa'))

    return render_template(
        'mahasiswa/edit.html',
        mahasiswa=mahasiswa
    )


@app.route('/mahasiswa/delete/<int:id>')
@login_required
@role_required('dosen')
def delete_mahasiswa(id):

    data = read_db()

    data['mahasiswa'] = [
        m for m in data['mahasiswa']
        if m['id'] != id
    ]

    write_db(data)

    return redirect(url_for('mahasiswa'))


# ======================================================
# DOSEN
# ======================================================
@app.route('/dosen')
@login_required
def dosen():

    data = read_db()

    return render_template(
        'dosen/index.html',
        dosen=data['dosen_data']
    )


@app.route('/dosen/tambah', methods=['GET', 'POST'])
@login_required
@role_required('superadmin')
def tambah_dosen():

    if request.method == 'POST':

        data = read_db()

        dosen = {
            "id": len(data['dosen_data']) + 1,
            "nama": request.form['nama'],
            "nidn": request.form['nidn'],
            "matkul": request.form['matkul']
        }

        data['dosen_data'].append(dosen)

        write_db(data)

        return redirect(url_for('dosen'))

    return render_template('dosen/add.html')


@app.route('/dosen/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('superadmin')
def edit_dosen(id):

    data = read_db()

    dosen = next(
        (d for d in data['dosen_data'] if d['id'] == id),
        None
    )

    if request.method == 'POST':

        dosen['nama'] = request.form['nama']
        dosen['nidn'] = request.form['nidn']
        dosen['matkul'] = request.form['matkul']

        write_db(data)

        return redirect(url_for('dosen'))

    return render_template(
        'dosen/edit.html',
        dosen=dosen
    )


@app.route('/dosen/delete/<int:id>')
@login_required
@role_required('superadmin')
def delete_dosen(id):

    data = read_db()

    data['dosen_data'] = [
        d for d in data['dosen_data']
        if d['id'] != id
    ]

    write_db(data)

    return redirect(url_for('dosen'))


# ======================================================
# USERS
# ======================================================
@app.route('/users')
@login_required
@role_required('superadmin')
def users():

    data = read_db()

    return render_template(
        'users.html',
        users=data['users']
    )


# ======================================================
# RUN
# ======================================================
if __name__ == '__main__':
    init_db()
    app.run(debug=True)