from flask import Blueprint, render_template, request, redirect, url_for, flash
from blueprints.utils import read_db, write_db, login_required, role_required

import hashlib
dosen_bp = Blueprint('dosen', __name__, url_prefix='/dosen')


@dosen_bp.route('/')
@login_required
def index():
    data = read_db()
    return render_template('dosen/index.html', dosen=data['dosen_data'])


@dosen_bp.route('/tambah', methods=['GET', 'POST'])
@login_required
@role_required('superadmin')
def tambah_dosen():

    if request.method == 'POST':

        data = read_db()

        hashed_password = hashlib.sha256(
            request.form['password'].encode()
        ).hexdigest()

        dosen = {
            "id": len(data['dosen_data']) + 1,
            "nama": request.form['nama'],
            "nidn": request.form['nidn'],
            "matkul": request.form['matkul'],
            "no_telp": request.form['no_telp']
        }

        user = {
            "id": len(data['users']) + 1,
            "username": request.form['nidn'],  # login pakai NIDN
            "password": hashed_password,
            "role": "dosen",
            "protected": False
        }

        data['dosen_data'].append(dosen)
        data['users'].append(user)

        write_db(data)

        flash('Dosen berhasil ditambahkan', 'success')

        return redirect(url_for('dosen'))

    return render_template('dosen/add.html')


@dosen_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('superadmin')
def edit_dosen(id):

    data = read_db()

    dosen = next(
        (d for d in data['dosen_data'] if d['id'] == id),
        None
    )

    if request.method == 'POST':

        old_nidn = dosen['nidn']

        dosen['nama'] = request.form['nama']
        dosen['nidn'] = request.form['nidn']
        dosen['matkul'] = request.form['matkul']
        dosen['no_telp'] = request.form['no_telp']

        user = next(
            (u for u in data['users']
             if u['username'] == old_nidn),
            None
        )

        if user:

            user['username'] = request.form['nidn']

            if request.form['password'] != '':
                user['password'] = hashlib.sha256(
                    request.form['password'].encode()
                ).hexdigest()

        write_db(data)

        flash('Dosen berhasil diupdate', 'success')

        return redirect(url_for('dosen'))

    return render_template(
        'dosen/edit.html',
        dosen=dosen
    )


@dosen_bp.route('/delete/<int:id>')
@login_required
@role_required('superadmin')
def delete(id):
    data = read_db()
    data['dosen_data'] = [d for d in data['dosen_data'] if d['id'] != id]
    write_db(data)
    return redirect(url_for('dosen'))

