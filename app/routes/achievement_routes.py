from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.services.achievement_service import AchievementService
from app.services.member_service import MemberService
from app.core.auth import get_current_user, login_required
from app.repositories.in_memory.branches_repo import branches_repo

achievement_bp = Blueprint('achievement', __name__, url_prefix='/achievement')

@achievement_bp.route('/add/<nomor_induk>', methods=['POST'])
def add(nomor_induk):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    data = {
        'nama_kejuaraan': request.form.get('nama_kejuaraan'),
        'kategori': request.form.get('kategori'),
        'tingkat': request.form.get('tingkat'),
        'medali': request.form.get('medali'),
        'tahun': request.form.get('tahun')
    }
    
    if all(data.values()):
        AchievementService.add_achievement(nomor_induk, data, session.get('user_id'))
        flash('Prestasi berhasil ditambahkan!', 'success')
    else:
        flash('Semua field harus diisi!', 'error')
        
    return redirect(url_for('kta.view', nomor_induk=nomor_induk))

@achievement_bp.route('/delete/<int:ach_id>', methods=['POST'])
def delete(ach_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    nomor_induk = request.form.get('nomor_induk')
    
    if AchievementService.delete_achievement(ach_id):
        flash('Prestasi berhasil dihapus.', 'success')
    else:
        flash('Gagal menghapus prestasi.', 'error')
        
    if nomor_induk:
        return redirect(url_for('kta.view', nomor_induk=nomor_induk))
    return redirect(url_for('dashboard.index'))

@achievement_bp.route('/pool')
@login_required
def pool():
    user = get_current_user()
    achievements = AchievementService.get_all_achievements()
    members = MemberService.get_all_members()
    member_map = {str(m.get('NOMOR INDUK', '')).strip(): m for m in members}
    branches = branches_repo.get_all_branches()
    
    enriched_achievements = []
    for ach in achievements:
        member = member_map.get(ach['nomor_induk'], {})
        ach['nama_lengkap'] = member.get('NAMA LENGKAP', 'Tidak diketahui')
        ach['cabang'] = member.get('CABANG', '-')
        ach['sabuk'] = member.get('SABUK', '-')
        enriched_achievements.append(ach)
        
    # 1. Hitung Statistik Ringkasan (Akumulasi Medali & Atlet)
    total_achievements = len(enriched_achievements)
    unique_athletes = len(set(ach['nomor_induk'] for ach in enriched_achievements if ach.get('nomor_induk')))
    total_emas = sum(1 for ach in enriched_achievements if str(ach.get('medali', '')).strip().lower() == 'emas')
    total_perak = sum(1 for ach in enriched_achievements if str(ach.get('medali', '')).strip().lower() == 'perak')
    total_perunggu = sum(1 for ach in enriched_achievements if str(ach.get('medali', '')).strip().lower() == 'perunggu')

    # 2. Filter dari Parameter URL
    search_query = request.args.get('search', '').strip()
    medali_filter = request.args.get('medali', '').strip()
    branch_filter = request.args.get('branch', '').strip()
    tingkat_filter = request.args.get('tingkat', '').strip()

    filtered = enriched_achievements

    # Jika admin_cabang, otomatis prioritaskan cabang mereka kecuali jika super_admin / admin_pusat
    if user and user.get('role') == 'admin_cabang':
        user_branch = branches_repo.get_branch(user.get('branch_code'))
        user_branch_name = user_branch['branch_name'].upper() if user_branch else (user.get('branch_code') or '').upper()
        # Biarkan admin cabang melihat cabang sendiri secara default, atau jika memilih filter
        if not branch_filter:
            branch_filter = user_branch_name

    if branch_filter:
        filtered = [a for a in filtered if str(a.get('cabang', '')).strip().upper() == branch_filter.upper()]

    if medali_filter:
        filtered = [a for a in filtered if str(a.get('medali', '')).strip().lower() == medali_filter.lower()]

    if tingkat_filter:
        filtered = [a for a in filtered if str(a.get('tingkat', '')).strip().lower() == tingkat_filter.lower()]

    if search_query:
        sq = search_query.lower()
        filtered = [
            a for a in filtered
            if sq in str(a.get('nama_lengkap', '')).lower()
            or sq in str(a.get('nomor_induk', '')).lower()
            or sq in str(a.get('nama_kejuaraan', '')).lower()
            or sq in str(a.get('kategori', '')).lower()
        ]

    # 3. Paginasi (10 per halaman)
    per_page = 10
    total_items = len(filtered)
    total_pages = max(1, (total_items + per_page - 1) // per_page)
    page = request.args.get('page', 1, type=int)
    page = max(1, min(page, total_pages)) if total_items > 0 else 1

    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, total_items)
    paginated_achievements = filtered[start_idx:end_idx]
    start_item = start_idx + 1 if total_items > 0 else 0

    return render_template(
        'achievement/pool.html',
        achievements=paginated_achievements,
        total_achievements=total_achievements,
        unique_athletes=unique_athletes,
        total_emas=total_emas,
        total_perak=total_perak,
        total_perunggu=total_perunggu,
        search_query=search_query,
        medali_filter=medali_filter,
        branch_filter=branch_filter,
        tingkat_filter=tingkat_filter,
        branches=branches,
        user=user,
        page=page,
        total_pages=total_pages,
        total_items=total_items,
        per_page=per_page,
        start_item=start_item,
        end_item=end_idx
    )
