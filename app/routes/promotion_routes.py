from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.core.auth import login_required, role_required
from app.services.promotion_service import PromotionService
from app.services.member_service import MemberService

promotion_bp = Blueprint('promotion', __name__, url_prefix='/promotions')

@promotion_bp.route('/wizard', methods=['GET', 'POST'])
@login_required
@role_required(['super_admin', 'admin_pusat']) # Only center admins can finalize promotions
def wizard():
    if request.method == 'POST':
        try:
            event_date = request.form.get('event_date')
            desa = request.form.get('desa').upper()
            kecamatan = request.form.get('kecamatan').upper()
            kabupaten = request.form.get('kabupaten').upper()
            
            # 1. Fetch new members from staging
            staging_members = PromotionService.fetch_staging_data()
            new_members = []
            for member in staging_members:
                new_members.append({
                    "nama_lengkap": str(member.get('NAMA LENGKAP', '')).strip().upper(),
                    "cabang": str(member.get('CABANG', '')).strip().upper(),
                    "new_level": "HIJAU", # Default to Hijau for new members
                    "ttl": member.get('TEMPAT TANGGAL LAHIR', ''),
                    "jenis_kelamin": str(member.get('JENIS KELAMIN', '')).strip().upper(),
                    "dusun": member.get('DUSUN/LINGKUNGAN', ''),
                    "desa": member.get('DESA/KELURAHAN', ''),
                    "kecamatan": member.get('KECAMATAN', ''),
                    "whatsapp": member.get('NOMOR WHATSAAP', ''),
                    "nomor_darurat": member.get('NOMOR DARURAT', '')
                })
                
            # 2. Get existing members being upgraded
            nomor_induks = request.form.getlist('nomor_induk[]')
            nama_lengkaps = request.form.getlist('nama_lengkap[]')
            target_belts = request.form.getlist('target_belt[]')
            
            upgrade_members = []
            for i in range(len(nomor_induks)):
                upgrade_members.append({
                    "nomor_induk": nomor_induks[i],
                    "nama_lengkap": nama_lengkaps[i],
                    "new_level": target_belts[i]
                })
                
            location = {"desa": desa, "kecamatan": kecamatan, "kabupaten": kabupaten}
            
            if new_members or upgrade_members:
                PromotionService.consolidated_promote(event_date, location, new_members, upgrade_members)
                
                # Clear caches so Data Induk and Staging updates immediately show
                try:
                    PromotionService.fetch_staging_data.clear_cache()
                    MemberService.get_all_members.clear_cache()
                except Exception:
                    pass
                    
                flash(f"Berhasil memproses! {len(new_members)} anggota baru dan {len(upgrade_members)} naik tingkat.", "success")
                return redirect(url_for('member.index'))
            else:
                flash("Tidak ada data baru di staging dan tidak ada anggota lama yang dipilih.", "warning")
            
        except Exception as e:
            flash(f"Gagal memproses: {str(e)}", "error")
            
    # For GET request, load staging and existing members
    staging_data = PromotionService.fetch_staging_data()
    if not staging_data:
        staging_data = []
        
    existing_members = MemberService.get_all_members()
        
    return render_template('promotions/wizard.html', staging_data=staging_data, existing_members=existing_members)
