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

    return render_template('kta/view.html', kta=kta_payload, user=user)

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

    branch_filter = request.args.get('branch', '')
    sabuk_filter = request.args.get('sabuk', '')

    if user['role'] == 'admin_cabang':
        branch_filter = branches_repo.get_branch(user['branch_code'])['branch_name']

    filtered = []
    host_url = request.host_url

    for m in members:
        if branch_filter and m.get('CABANG', '').upper() != branch_filter.upper():
            continue
        if sabuk_filter and str(m.get('SABUK', '')).strip().upper() != sabuk_filter.upper():
            continue

        payload = KtaService.prepare_kta_payload(m, host_url)
        filtered.append(payload)

    # Pagination (10 per page)
    per_page = 10
    total_items = len(filtered)
    total_pages = max(1, (total_items + per_page - 1) // per_page)
    page = request.args.get('page', 1, type=int)
    page = max(1, min(page, total_pages)) if total_items > 0 else 1

    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, total_items)
    paginated_items = filtered[start_idx:end_idx]
    start_item = start_idx + 1 if total_items > 0 else 0

    return render_template('kta/batch.html',
                           items=paginated_items,
                           branches=branches,
                           current_branch=branch_filter,
                           current_sabuk=sabuk_filter,
                           user=user,
                           page=page,
                           total_pages=total_pages,
                           total_items=total_items,
                           per_page=per_page,
                           start_item=start_item,
                           end_item=end_idx)
