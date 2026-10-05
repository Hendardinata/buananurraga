import urllib.parse
from flask import Blueprint, redirect, request, flash, url_for
from app.core.auth import login_required, get_current_user
from app.services.member_service import MemberService
from app.core.normalizer import DataNormalizer

whatsapp_bp = Blueprint('whatsapp', __name__, url_prefix='/whatsapp')

@whatsapp_bp.route('/dispatch/<nomor_induk>')
@login_required
def dispatch(nomor_induk):
    member = MemberService.get_member_by_id(nomor_induk)
    
    if not member:
        flash("Anggota tidak ditemukan.", "danger")
        return redirect(url_for('member.index'))

    # Clean and extract phone number
    raw_phone = member.get('NOMOR WHATSAAP') or member.get('NOMOR DARURAT') or ''
    cleaned_phone = DataNormalizer.clean_phone_number(str(raw_phone))

    # Format international standard for Indonesia (replace 08 -> 628)
    digits = ''.join(c for c in cleaned_phone if c.isdigit())
    if digits.startswith('0'):
        digits = '62' + digits[1:]
    elif not digits.startswith('62') and len(digits) >= 8:
        digits = '62' + digits

    nama = member.get('NAMA LENGKAP', '').strip().upper()
    sabuk = member.get('SABUK', 'HIJAU')
    tanggal_sah = member.get(sabuk) or member.get('HIJAU') or '25 Mei 2025'
    host = request.host_url.rstrip('/')

    kta_url = f"{host}/kta/view/{nomor_induk}"
    verify_url = f"{host}/verify/{nomor_induk}"

    message = (
        f"Salam Perguruan Silat Buana Nurraga.\n\n"
        f"Selamat kepada Saudara *{nama}* atas kelulusan pengesahan tingkatan *{sabuk}* pada tanggal {tanggal_sah}.\n\n"
        f"Kartu Tanda Anggota (KTA) Digital resmi Anda telah terbit dan dapat diakses melalui tautan berikut:\n"
        f"🪪 *Lihat KTA Digital:* {kta_url}\n\n"
        f"🔍 *Cek Keaslian Resmi (Verifikasi QR):* {verify_url}\n\n"
        f"Mohon simpan dan jaga identitas keanggotaan Anda dengan penuh kehormatan.\n\n"
        f"— *Dewan Pimpinan Pusat Perguruan Silat Buana Nurraga*"
    )

    encoded_msg = urllib.parse.quote(message)

    if not digits or len(digits) < 9:
        flash(f"Nomor WhatsApp untuk {nama} belum tercatat di data anggota. Anda dapat membagikan link KTA secara manual: {kta_url}", "warning")
        return redirect(url_for('kta.view', nomor_induk=nomor_induk))

    wa_url = f"https://api.whatsapp.com/send?phone={digits}&text={encoded_msg}"
    return redirect(wa_url)
