from flask import Blueprint, render_template, session
from app.core.auth import login_required
from app.services.member_service import MemberService
from app.core.auth import get_current_user

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    user = get_current_user()
    members = MemberService.get_all_members()
    
    # Filter members by branch if user is an admin_cabang
    if user['role'] == 'admin_cabang':
        from app.repositories.in_memory.branches_repo import branches_repo
        branch = branches_repo.get_branch(user['branch_code'])
        branch_name_upper = branch['branch_name'].upper() if branch else ''
        members = [m for m in members if m.get('CABANG', '').upper() == branch_name_upper]
        
    total_members = len(members)
    punya_kta = sum(1 for m in members if str(m.get('KTA', '')).strip().upper() == 'PUNYA')
    
    # Sabuk distribution
    sabuk_counts = {}
    branch_counts = {}
    for m in members:
        sabuk = str(m.get('SABUK', '')).strip().upper()
        if sabuk:
            sabuk_counts[sabuk] = sabuk_counts.get(sabuk, 0) + 1
            
        cabang = str(m.get('CABANG', '')).strip().upper()
        if cabang:
            branch_counts[cabang] = branch_counts.get(cabang, 0) + 1
            
    return render_template('dashboard/index.html', 
                          total_members=total_members,
                          punya_kta=punya_kta,
                          sabuk_counts=sabuk_counts,
                          branch_counts=branch_counts,
                          user=user)
