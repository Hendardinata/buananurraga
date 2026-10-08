from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, abort
from app.core.auth import login_required, get_current_user
from app.services.member_service import MemberService
from app.services.kta_service import KtaService
from app.repositories.in_memory.branches_repo import branches_repo

kta_bp = Blueprint('kta', __name__, url_prefix='/kta')

@kta_bp.route('/view/<nomor_induk>')
@login_required
def view(nomor_induk):
    user = get_current_user()
    member = MemberService.get_member_by_id(nomor_induk)
    
    if not member:
        flash(f"Anggota dengan Nomor Induk '{nomor_induk}' tidak ditemukan.", "danger")
        return redirect(url_for('member.index'))

    # Branch authorization check
    if user['role'] == 'admin_cabang':
        branch_info = branches_repo.get_branch(user['branch_code'])
        if branch_info and member.get('CABANG', '').upper() != branch_info['branch_name'].upper():
            abort(403)

    host_url = request.host_url
    kta_payload = KtaService.prepare_kta_payload(member, host_url)

    from app.services.achievement_service import AchievementService
    achievements = AchievementService.get_achievements_by_nomor_induk(nomor_induk)

    return render_template('kta/view.html', kta=kta_payload, user=user, achievements=achievements)

@kta_bp.route('/download/<nomor_induk>')
@login_required
def download_png(nomor_induk):
    user = get_current_user()
    member = MemberService.get_member_by_id(nomor_induk)
    
    if not member:
        abort(404)

    # Branch authorization check
    if user['role'] == 'admin_cabang':
        branch_info = branches_repo.get_branch(user['branch_code'])
        if branch_info and member.get('CABANG', '').upper() != branch_info['branch_name'].upper():
            abort(403)

    side = request.args.get('side', 'front').lower()
    if side not in ['front', 'back']:
        side = 'front'

    host_url = request.host_url
    img_buffer = KtaService.generate_server_png(member, host_url, side=side)

    clean_id = str(nomor_induk).replace(' ', '_').replace('/', '_')
    filename = f"KTA_BN_{clean_id}_{side.upper()}.png"

    return send_file(
        img_buffer,
        mimetype="image/png",
        as_attachment=True,
        download_name=filename
    )

@kta_bp.route('/mark-physical/<nomor_induk>', methods=['POST'])
@login_required
def mark_physical(nomor_induk):
    user = get_current_user()
    member = MemberService.get_member_by_id(nomor_induk)
    
    if not member:
        flash("Anggota tidak ditemukan.", "danger")
        return redirect(url_for('member.index'))

    if user['role'] == 'admin_cabang':
        branch_info = branches_repo.get_branch(user['branch_code'])
        if branch_info and member.get('CABANG', '').upper() != branch_info['branch_name'].upper():
            abort(403)

    try:
        MemberService.update_kta_status(nomor_induk, status="PUNYA")
        flash(f"Status KTA fisik untuk {member.get('NAMA LENGKAP')} berhasil diperbarui menjadi 'PUNYA'!", "success")
    except Exception as e:
        flash(f"Gagal memperbarui status ke Google Sheets: {str(e)}", "danger")

    return redirect(url_for('kta.view', nomor_induk=nomor_induk))

@kta_bp.route('/batch')
@login_required
def batch():
    user = get_current_user()
    members = MemberService.get_all_members()
    branches = branches_repo.get_all_branches()

    # 1. Hitung Statistik Ringkasan KTA
    total_all_members = len(members)
    total_kta_printed = sum(1 for m in members if str(m.get('KTA', '')).strip().upper() == 'PUNYA')
    total_kta_pending = sum(1 for m in members if str(m.get('KTA', '')).strip().upper() != 'PUNYA')

    # 2. Filter & Pencarian
    search_query = request.args.get('search', '').strip()
    branch_filter = request.args.get('branch', '').strip()
    sabuk_filter = request.args.get('sabuk', '').strip()
    status_filter = request.args.get('status', '').strip().upper()

    if user['role'] == 'admin_cabang':
        branch_info = branches_repo.get_branch(user['branch_code'])
        branch_filter = branch_info['branch_name'] if branch_info else user.get('branch_code', '')

    filtered_members = []
    for m in members:
        if branch_filter and str(m.get('CABANG', '')).strip().upper() != branch_filter.upper():
            continue
        if sabuk_filter and str(m.get('SABUK', '')).strip().upper() != sabuk_filter.upper():
            continue
        if status_filter:
            m_kta = str(m.get('KTA', '')).strip().upper()
            if status_filter == 'PUNYA' and m_kta != 'PUNYA':
                continue
            if status_filter == 'BELUM' and m_kta == 'PUNYA':
                continue
        if search_query:
            sq = search_query.lower()
            name = str(m.get('NAMA LENGKAP', '')).lower()
            nik = str(m.get('NOMOR INDUK', '')).lower()
            desa = str(m.get('DESA', '')).lower()
            if sq not in name and sq not in nik and sq not in desa:
                continue
        filtered_members.append(m)

    # 3. Paginasi (12 per halaman, presisi untuk grid 3 kolom)
    per_page = 12
    total_items = len(filtered_members)
    total_pages = max(1, (total_items + per_page - 1) // per_page)
    page = request.args.get('page', 1, type=int)
    page = max(1, min(page, total_pages)) if total_items > 0 else 1

    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, total_items)
    paginated_members = filtered_members[start_idx:end_idx]
    start_item = start_idx + 1 if total_items > 0 else 0

    # 4. Generate KTA Payload untuk item halaman aktif
    host_url = request.host_url
    paginated_items = [KtaService.prepare_kta_payload(m, host_url) for m in paginated_members]

    return render_template(
        'kta/batch.html',
        items=paginated_items,
        total_all_members=total_all_members,
        total_kta_printed=total_kta_printed,
        total_kta_pending=total_kta_pending,
        search_query=search_query,
        branches=branches,
        current_branch=branch_filter,
        current_sabuk=sabuk_filter,
        current_status=status_filter,
        user=user,
        page=page,
        total_pages=total_pages,
        total_items=total_items,
        per_page=per_page,
        start_item=start_item,
        end_item=end_idx
    )
