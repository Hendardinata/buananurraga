from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.user import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Akun Anda tidak aktif.', 'error')
                return redirect(url_for('auth.login'))
                
            from datetime import datetime, timedelta
            import uuid
            from app.extensions import db
            
            # Check for active session (e.g. active within last 30 minutes)
            if user.session_token and user.last_active:
                if datetime.utcnow() - user.last_active < timedelta(minutes=30):
                    flash('Akun ini sedang login di perangkat lain. Harap tunggu atau logout dari perangkat tersebut.', 'error')
                    return redirect(url_for('auth.login'))
            
            new_token = str(uuid.uuid4())
            user.session_token = new_token
            user.last_active = datetime.utcnow()
            db.session.commit()
                
            session['user_id'] = user.username
            session['role'] = user.role
            session['full_name'] = user.full_name
            session['session_token'] = new_token
            
            # Redirect to dashboard
            return redirect(url_for('dashboard.index'))
        else:
            flash('Username atau password salah.', 'error')
            
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    if 'user_id' in session:
        from app.extensions import db
        user = User.query.filter_by(username=session['user_id']).first()
        if user and session.get('session_token') == user.session_token:
            user.session_token = None
            db.session.commit()
    session.clear()
    return redirect(url_for('auth.login'))
