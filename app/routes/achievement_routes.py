from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.services.achievement_service import AchievementService
from app.services.member_service import MemberService

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
def pool():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    achievements = AchievementService.get_all_achievements()
    
    # We need to attach member data (nama_lengkap, cabang) to achievements for the dashboard
    # Since get_all_members is cached or fast enough in MemberService (wait, it fetches from GAS!)
    # Fetching all members from GAS every time might be slow if there are many. 
    # For now, let's just fetch all members and map them.
    members = MemberService.get_all_members()
    member_map = {str(m.get('NOMOR INDUK', '')).strip(): m for m in members}
    
    enriched_achievements = []
    for ach in achievements:
        member = member_map.get(ach['nomor_induk'], {})
        ach['nama_lengkap'] = member.get('NAMA LENGKAP', 'Tidak diketahui')
        ach['cabang'] = member.get('CABANG', '-')
        ach['sabuk'] = member.get('SABUK', '-')
        enriched_achievements.append(ach)
        
    return render_template('achievement/pool.html', achievements=enriched_achievements)
