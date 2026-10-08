from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from app.models.user import User
from app.extensions import db
from app.core.auth import login_required, role_required, get_current_user
from app.repositories.in_memory.branches_repo import branches_repo

user_bp = Blueprint('user', __name__, url_prefix='/users')

def format_last_active(dt):
    if not dt:
        return "Belum pernah aktif"
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']
    return f"{dt.day:02d} {months[dt.month - 1]} {dt.year}, {dt.strftime('%H:%M')} WITA"

@user_bp.route('/')
@login_required
@role_required('super_admin')
def index():
    current_user = get_current_user()
    all_users = User.query.order_by(User.id.asc()).all()
    branches = branches_repo.get_all_branches()
    branch_map = {b['branch_code']: b['branch_name'] for b in branches}

    # 1. Hitung Statistik Ringkasan Pengguna
    total_users = len(all_users)
    total_super_admin = sum(1 for u in all_users if u.role == 'super_admin')
    total_admin_pusat = sum(1 for u in all_users if u.role == 'admin_pusat')
    total_admin_cabang = sum(1 for u in all_users if u.role == 'admin_cabang')
    total_active = sum(1 for u in all_users if u.is_active)

    # 2. Filter & Pencarian
    search_query = request.args.get('search', '').strip()
    role_filter = request.args.get('role', '').strip()
    status_filter = request.args.get('status', '').strip()
    branch_filter = request.args.get('branch', '').strip()

    filtered = all_users
    if search_query:
        sq = search_query.lower()
        filtered = [
            u for u in filtered
            if sq in u.username.lower() or sq in u.full_name.lower() or (u.branch_code and sq in u.branch_code.lower())
        ]
    if role_filter:
        filtered = [u for u in filtered if u.role == role_filter]
    if status_filter:
        if status_filter == 'active':
            filtered = [u for u in filtered if u.is_active]
        elif status_filter == 'inactive':
            filtered = [u for u in filtered if not u.is_active]
    if branch_filter:
        filtered = [u for u in filtered if u.branch_code and u.branch_code.upper() == branch_filter.upper()]

    # 3. Format Data untuk Tampilan
    enriched_users = []
    for u in filtered:
        branch_display = "Pusat"
        if u.role == 'admin_cabang':
            code = u.branch_code or "-"
            name = branch_map.get(code, code)
            branch_display = f"{name} ({code})" if name != code else code

        enriched_users.append({
            'id': u.id,
            'username': u.username,
            'full_name': u.full_name,
            'role': u.role,
            'branch_code': u.branch_code,
            'branch_display': branch_display,
            'is_active': u.is_active,
            'last_active_formatted': format_last_active(u.last_active)
        })

    # 4. Paginasi (10 per halaman)
    per_page = 10
    total_items = len(enriched_users)
    total_pages = max(1, (total_items + per_page - 1) // per_page)
    page = request.args.get('page', 1, type=int)
    page = max(1, min(page, total_pages)) if total_items > 0 else 1

    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, total_items)
    paginated_users = enriched_users[start_idx:end_idx]
    start_item = start_idx + 1 if total_items > 0 else 0

    return render_template(
        'users/index.html',
        users=paginated_users,
        total_users=total_users,
        total_super_admin=total_super_admin,
        total_admin_pusat=total_admin_pusat,
        total_admin_cabang=total_admin_cabang,
        total_active=total_active,
        search_query=search_query,
        role_filter=role_filter,
        status_filter=status_filter,
        branch_filter=branch_filter,
        branches=branches,
        user=current_user,
        page=page,
        total_pages=total_pages,
        total_items=total_items,
        per_page=per_page,
        start_item=start_item,
        end_item=end_idx
    )

@user_bp.route('/add', methods=['POST'])
@login_required
@role_required('super_admin')
def add_user():
    username = request.form.get('username', '').strip().lower()
    password = request.form.get('password', '').strip()
    full_name = request.form.get('full_name', '').strip()
    role = request.form.get('role', 'admin_cabang').strip()
    branch_code = request.form.get('branch_code', '').strip().upper() if role == 'admin_cabang' else None
    
    if not username or not password or not full_name:
        flash('Username, password, dan nama lengkap wajib diisi!', 'error')
        return redirect(url_for('user.index'))

    if len(password) < 6:
        flash('Password baru minimal 6 karakter!', 'error')
        return redirect(url_for('user.index'))

    if User.query.filter_by(username=username).first():
        flash(f'Username "{username}" sudah digunakan.', 'error')
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
    
    flash(f'Pengguna {username} berhasil ditambahkan!', 'success')
    return redirect(url_for('user.index'))

@user_bp.route('/toggle/<int:id>', methods=['POST'])
@login_required
@role_required('super_admin')
def toggle_user(id):
    user = User.query.get_or_404(id)
    
    if user.username == 'superadmin':
        flash('Tidak dapat menonaktifkan akun utama sistem.', 'error')
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
        flash('Tidak dapat menghapus akun utama sistem.', 'error')
        return redirect(url_for('user.index'))
        
    db.session.delete(user)
    db.session.commit()
    
    flash(f'Akun {user.username} berhasil dihapus permanen.', 'success')
    return redirect(url_for('user.index'))

@user_bp.route('/reset_password/<int:id>', methods=['POST'])
@login_required
@role_required('super_admin')
def reset_password(id):
    user = User.query.get_or_404(id)
    new_password = request.form.get('new_password', '').strip()
    
    if not new_password or len(new_password) < 6:
        flash('Password baru minimal 6 karakter.', 'error')
        return redirect(url_for('user.index'))
        
    user.set_password(new_password)
    db.session.commit()
    
    flash(f'Password untuk pengguna {user.username} berhasil diperbarui.', 'success')
    return redirect(url_for('user.index'))
