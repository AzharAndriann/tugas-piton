from flask import Blueprint, render_template, request, redirect, url_for
from blueprints.utils import read_db, write_db, login_required

matakuliah_bp = Blueprint('matakuliah', __name__, url_prefix='/matakuliah')


@matakuliah_bp.route('/')
@login_required
def index():
    data = read_db()
    return render_template('matakuliah/index.html', data_mk=data['mata_kuliah'])


@matakuliah_bp.route('/tambah', methods=['GET', 'POST'])
@login_required
def tambah():
    if request.method == 'POST':
        data = read_db()
        data['mata_kuliah'].append({
            "kode_matkul": int(request.form['kode_matkul']),
            "nama_mk": request.form['nama_mk'],
            "fakultas": request.form['fakultas'],
            "sks": request.form['sks']
        })
        write_db(data)
        return redirect(url_for('matakuliah.index'))
    return render_template('matakuliah/add.html')


@matakuliah_bp.route('/edit/<int:kode_matkul>', methods=['GET', 'POST'])
@login_required
def edit(kode_matkul):
    data = read_db()
    mk = next((x for x in data['mata_kuliah'] if x['kode_matkul'] == kode_matkul), None)
    if request.method == 'POST':
        mk['nama_mk'] = request.form['nama_mk']
        mk['fakultas'] = request.form['fakultas']
        mk['sks'] = request.form['sks']
        write_db(data)
        return redirect(url_for('matakuliah.index'))
    return render_template('matakuliah/edit.html', mk=mk)


@matakuliah_bp.route('/delete/<int:kode_matkul>')
@login_required
def delete(kode_matkul):
    data = read_db()
    data['mata_kuliah'] = [x for x in data['mata_kuliah'] if x['kode_matkul'] != kode_matkul]
    write_db(data)
    return redirect(url_for('matakuliah.index'))