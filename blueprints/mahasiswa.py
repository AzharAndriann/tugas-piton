from flask import Blueprint, render_template, request, redirect, url_for
from blueprints.utils import read_db, write_db, login_required, role_required
import hashlib

mahasiswa_bp = Blueprint('mahasiswa', __name__, url_prefix='/mahasiswa')

ROLES_MAHASISWA = ['ketua', 'wakil', 'sekretaris']


@mahasiswa_bp.route('/')
@login_required
def index():
    data = read_db()
    return render_template('mahasiswa/index.html', mahasiswa=data['mahasiswa'])



@mahasiswa_bp.route('/tambah', methods=['GET', 'POST'])
@login_required
@role_required('dosen')
def tambah():
    if request.method == 'POST':
        data = read_db()

        new_id = max((m['id'] for m in data['mahasiswa']), default=0) + 1

        data['mahasiswa'].append({
            "id": new_id,
            "nama": request.form['nama'],
            "npm": request.form['npm'],
            "password": hashlib.sha256(
                request.form['password'].encode()
            ).hexdigest(),
            "no_telp": request.form['no_telp'],
            "role": request.form['role']
        })

        write_db(data)

        return redirect(url_for('mahasiswa.index'))

    return render_template('mahasiswa/add.html', roles=ROLES_MAHASISWA)



@mahasiswa_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('dosen')
def edit(id):
    data = read_db()

    mhs = next((m for m in data['mahasiswa'] if m['id'] == id), None)

    if request.method == 'POST':
        mhs['nama'] = request.form['nama']
        mhs['npm'] = request.form['npm']
        mhs['no_telp'] = request.form['no_telp']
        mhs['role'] = request.form['role']
        mhs['password'] = request.form['password']

        write_db(data)

        return redirect(url_for('mahasiswa.index'))

    return render_template(
        'mahasiswa/edit.html',
        mahasiswa=mhs,
        roles=ROLES_MAHASISWA
    )


@mahasiswa_bp.route('/delete/<int:id>')
@login_required
@role_required('dosen')
def delete(id):
    data = read_db()
    data['mahasiswa'] = [m for m in data['mahasiswa'] if m['id'] != id]
    write_db(data)
    return redirect(url_for('mahasiswa.index'))