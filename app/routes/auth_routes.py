from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.repositories.in_memory.users_repo import users_repo

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if users_repo.verify_password(username, password):
            user = users_repo.get_user_by_username(username)
            if user['status'] != 'ACTIVE':
                flash('Akun Anda tidak aktif.', 'error')
                return redirect(url_for('auth.login'))
                
            session['user_id'] = username
            session['role'] = user['role']
            session['full_name'] = user['full_name']
            
            # Redirect to dashboard
            return redirect(url_for('dashboard.index'))
        else:
            flash('Username atau password salah.', 'error')
            
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
