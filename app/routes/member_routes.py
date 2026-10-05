from flask import Blueprint, render_template, request
from app.core.auth import login_required, get_current_user
from app.services.member_service import MemberService
from app.repositories.in_memory.branches_repo import branches_repo

member_bp = Blueprint('member', __name__, url_prefix='/members')

@member_bp.route('/')
@login_required
def index():
    user = get_current_user()
    members = MemberService.get_all_members()
    branches = branches_repo.get_all_branches()
    
    # Get filters
    search_query = request.args.get('search', '').lower()
    branch_filter = request.args.get('branch', '')
    sabuk_filter = request.args.get('sabuk', '')
    
    # Apply Role-Based filtering
    if user['role'] == 'admin_cabang':
        branch_filter = user['branch_code']
        
    filtered_members = []
    for member in members:
        # Branch Filter
        if branch_filter:
            branch_info = branches_repo.get_branch(branch_filter)
            if branch_info and member.get('CABANG', '').upper() != branch_info['branch_name'].upper():
                continue
            
        # Sabuk Filter
        if sabuk_filter and str(member.get('SABUK')).strip().upper() != sabuk_filter.upper():
            continue
            
        # Search Filter (No Induk, Nama, atau Desa)
        if search_query:
            no_induk = str(member.get('NOMOR INDUK', '')).lower()
            nama = str(member.get('NAMA LENGKAP', '')).lower()
            desa = str(member.get('DESA/KELURAHAN', '')).lower()
            if search_query not in no_induk and search_query not in nama and search_query not in desa:
                continue
                
        filtered_members.append(member)
        
    # Pagination (10 per page)
    per_page = 10
    total_items = len(filtered_members)
    total_pages = max(1, (total_items + per_page - 1) // per_page)
    page = request.args.get('page', 1, type=int)
    page = max(1, min(page, total_pages)) if total_items > 0 else 1
    
    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, total_items)
    paginated_members = filtered_members[start_idx:end_idx]
    start_item = start_idx + 1 if total_items > 0 else 0
        
    return render_template('members/index.html', 
                          members=paginated_members,
                          branches=branches,
                          user=user,
                          current_branch_filter=branch_filter,
                          current_sabuk_filter=sabuk_filter,
                          current_search=search_query,
                          page=page,
                          total_pages=total_pages,
                          total_items=total_items,
                          per_page=per_page,
                          start_item=start_item,
                          end_item=end_idx)

@member_bp.route('/<nomor_induk>')
@login_required
def detail(nomor_induk):
    user = get_current_user()
    member = MemberService.get_member_by_id(nomor_induk)
    
    if not member:
        return {'error': 'Member not found'}, 404
        
    # Check access permission
    if user['role'] == 'admin_cabang' and member.get('CABANG') != user['branch_code']:
        return {'error': 'Unauthorized access to this member'}, 403
        
    # Return as partial HTML for modal or a full page
    return render_template('members/_detail_modal.html', member=member)
