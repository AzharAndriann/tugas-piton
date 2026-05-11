from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from blueprints.utils import read_db
import hashlib

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = hashlib.sha256(
            request.form['password'].encode()
        ).hexdigest()

        data = read_db()

        # =========================
        # LOGIN USER ADMIN / DOSEN
        # =========================
        user = next(
            (
                u for u in data['users']
                if u['username'] == username
                and u['password'] == password
            ),
            None
        )

        if user:

            session['logged_in'] = True
            session['username'] = user['username']
            session['role'] = user['role']

            flash('Login berhasil', 'success')

            return redirect(url_for('matakuliah.index'))

        # =========================
        # LOGIN MAHASISWA
        # username input = npm
        # =========================
        mahasiswa = next(
            (
                m for m in data['mahasiswa']
                if m['npm'] == username
                and m['password'] == password
            ),
            None
        )

        if mahasiswa:

            session['logged_in'] = True
            session['username'] = mahasiswa['nama']
            session['role'] = 'mahasiswa'
            session['npm'] = mahasiswa['npm']

            flash('Login mahasiswa berhasil', 'success')

            return redirect(url_for('mahasiswa.index'))

        flash('Username / Password salah', 'error')

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():

    session.clear()

    flash('Berhasil logout', 'success')

    return redirect(url_for('auth.login'))