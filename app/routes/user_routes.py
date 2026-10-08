from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.user import User
from app.extensions import db
from app.core.auth import login_required, role_required
from werkzeug.security import generate_password_hash

user_bp = Blueprint('user', __name__, url_prefix='/users')

@user_bp.route('/')
@login_required
@role_required('super_admin')
def index():
    users = User.query.all()
    return render_template('users/index.html', users=users)

@user_bp.route('/add', methods=['POST'])
@login_required
@role_required('super_admin')
def add_user():
    username = request.form.get('username')
    password = request.form.get('password')
    full_name = request.form.get('full_name')
    role = request.form.get('role')
    branch_code = request.form.get('branch_code') or None
    
    if User.query.filter_by(username=username).first():
        flash('Username sudah digunakan.', 'error')
        return redirect(url_for('user.index'))
        
    new_user = User(
        username=username,
        full_name=full_name,
        role=role,
        branch_code=branch_code
    )
    new_user.set_password(password)
    
    db.session.add(new_user)
    db.session.commit()
    
    flash('Pengguna berhasil ditambahkan.', 'success')
    return redirect(url_for('user.index'))

@user_bp.route('/toggle/<int:id>', methods=['POST'])
@login_required
@role_required('super_admin')
def toggle_user(id):
    user = User.query.get_or_404(id)
    
    if user.username == 'superadmin':
        flash('Tidak dapat menonaktifkan akun utama.', 'error')
        return redirect(url_for('user.index'))
        
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'diaktifkan' if user.is_active else 'dinonaktifkan'
    flash(f'Akun {user.username} berhasil {status}.', 'success')
    return redirect(url_for('user.index'))
    
@user_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
@role_required('super_admin')
def delete_user(id):
    user = User.query.get_or_404(id)
    
    if user.username == 'superadmin':
        flash('Tidak dapat menghapus akun utama.', 'error')
        return redirect(url_for('user.index'))
        
    db.session.delete(user)
    db.session.commit()
    
    flash(f'Akun {user.username} berhasil dihapus.', 'success')
    return redirect(url_for('user.index'))

@user_bp.route('/reset_password/<int:id>', methods=['POST'])
@login_required
@role_required('super_admin')
def reset_password(id):
    user = User.query.get_or_404(id)
    new_password = request.form.get('new_password')
    
    if not new_password or len(new_password) < 6:
        flash('Password baru minimal 6 karakter.', 'error')
        return redirect(url_for('user.index'))
        
    user.set_password(new_password)
    db.session.commit()
    
    flash(f'Password untuk pengguna {user.username} berhasil diperbarui.', 'success')
    return redirect(url_for('user.index'))
