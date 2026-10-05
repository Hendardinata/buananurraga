from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.core.auth import login_required, get_current_user
from app.repositories.google_sheet.gas_client import GasClient
from app.repositories.in_memory.branches_repo import branches_repo
from datetime import datetime

staging_bp = Blueprint('staging', __name__, url_prefix='/staging')

@staging_bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    user = get_current_user()
    branches = branches_repo.get_all_branches()
    
    if request.method == 'POST':
        try:
            # Construct member data according to GAS format
            member_data = {
                "tanggal_naik": request.form.get('tanggal_naik', datetime.now().strftime('%d/%m/%Y')),
                "urutan": "", # Will be assigned during finalization
                "cabang": request.form.get('cabang'),
                "nama_lengkap": request.form.get('nama_lengkap').upper(),
                "ttl": f"{request.form.get('tempat_lahir').upper()}, {request.form.get('tanggal_lahir')}",
                "jenis_kelamin": request.form.get('jenis_kelamin'),
                "dusun": request.form.get('dusun').upper(),
                "desa": request.form.get('desa').upper(),
                "kecamatan": request.form.get('kecamatan').upper(),
                "whatsapp": request.form.get('whatsapp'),
                "nomor_darurat": request.form.get('nomor_darurat')
            }
            
            # Send to GAS
            GasClient.add_member_to_staging(member_data)
            
            flash('Berhasil mendaftarkan calon anggota ke Data Mentah!', 'success')
            return redirect(url_for('member.index'))
            
        except Exception as e:
            flash(f'Terjadi kesalahan: {str(e)}', 'error')
            
    return render_template('staging/register.html', user=user, branches=branches)
