from datetime import datetime
from flask import Blueprint, render_template, request
from app.services.member_service import MemberService
from app.services.kta_service import KtaService

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def index():
    return render_template('public/index.html')

@public_bp.route('/verify/<nomor_induk>')
def verify(nomor_induk):
    """
    Public verification endpoint accessed by scanning the QR code on a member's KTA.
    No login required. Sensitive personal data (NIK, address details, contacts) are hidden.
    """
    member = MemberService.get_member_by_id(nomor_induk)
    now_str = datetime.now().strftime("%d %B %Y, %H:%M:%S WITA")

    if not member:
        return render_template(
            'public/verify.html',
            is_valid=False,
            nomor_induk=nomor_induk,
            checked_at=now_str
        ), 404

    sabuk = str(member.get('SABUK', 'HIJAU')).strip().upper()
    belt_info = KtaService.get_belt_info(sabuk)

    tanggal_sah = member.get(sabuk)
    if not tanggal_sah or str(tanggal_sah).strip() == '':
        tanggal_sah = member.get('HIJAU') or member.get('TANGGAL') or '25 Mei 2025'

    member_data = {
        'nama_lengkap': str(member.get('NAMA LENGKAP', '')).strip().upper(),
        'nomor_induk': str(member.get('NOMOR INDUK', '')).strip(),
        'sabuk': sabuk,
        'belt_info': belt_info,
        'cabang': str(member.get('CABANG', '-')).strip(),
        'kabupaten': str(member.get('KABUPATEN/KOTA', member.get('CABANG', '-'))).strip(),
        'tanggal_sah': str(tanggal_sah).strip(),
        'photo_url': member.get('FOTO_URL') or '/static/img/avatar_placeholder.svg',
    }

    from app.services.achievement_service import AchievementService
    achievements = AchievementService.get_achievements_by_nomor_induk(nomor_induk)

    return render_template(
        'public/verify.html',
        is_valid=True,
        member_data=member_data,
        nomor_induk=nomor_induk,
        checked_at=now_str,
        achievements=achievements
    )
