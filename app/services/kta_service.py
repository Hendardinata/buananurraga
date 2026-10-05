import io
import os
from flask import url_for
from app.core.qr_generator import QRGenerator
from PIL import Image, ImageDraw, ImageFont

class KtaService:
    """
    Service for generating high-class, luxury digital KTA (Front & Back)
    for members of Perguruan Silat Buana Nurraga.
    """

    BELT_CONFIG = {
        'HIJAU': {
            'label': 'SABUK HIJAU',
            'bg_gradient': 'linear-gradient(135deg, #1b5e20, #2e7d32)',
            'color': '#4caf50',
            'level_name': 'Tingkat Pengesahan Awal',
            'rank_order': 1
        },
        'BIRU': {
            'label': 'SABUK BIRU',
            'bg_gradient': 'linear-gradient(135deg, #0d47a1, #1976d2)',
            'color': '#2196f3',
            'level_name': 'Tingkat Madya I',
            'rank_order': 2
        },
        'COKELAT': {
            'label': 'SABUK COKELAT',
            'bg_gradient': 'linear-gradient(135deg, #3e2723, #6d4c41)',
            'color': '#8d6e63',
            'level_name': 'Tingkat Madya II (Pra-Pelatih)',
            'rank_order': 3
        },
        'HITAM COKELAT': {
            'label': 'SABUK HITAM COKELAT',
            'bg_gradient': 'linear-gradient(135deg, #26160e, #5d4037)',
            'color': '#d7ccc8',
            'level_name': 'Pelatih Perguruan',
            'rank_order': 4
        },
        'HITAM ORANGE': {
            'label': 'SABUK HITAM ORANGE',
            'bg_gradient': 'linear-gradient(135deg, #212121, #e65100)',
            'color': '#ff9800',
            'level_name': 'Pelatih Utama',
            'rank_order': 5
        },
        'GURU': {
            'label': 'DEWAN GURU',
            'bg_gradient': 'linear-gradient(135deg, #b8860b, #d4af37)',
            'color': '#ffd54f',
            'level_name': 'Dewan Guru Keilmuan',
            'rank_order': 6
        },
        'GURU BESAR': {
            'label': 'GURU BESAR',
            'bg_gradient': 'linear-gradient(135deg, #7c5806, #d4af37, #ffe082)',
            'color': '#ffe082',
            'level_name': 'Pimpinan Tertinggi Keilmuan',
            'rank_order': 7
        }
    }

    @classmethod
    def get_belt_info(cls, sabuk_name: str) -> dict:
        key = str(sabuk_name).strip().upper()
        return cls.BELT_CONFIG.get(key, {
            'label': key or 'ANGGOTA RESMI',
            'bg_gradient': 'linear-gradient(135deg, #2c3e50, #4ca1af)',
            'color': '#ffffff',
            'level_name': 'Anggota Perguruan',
            'rank_order': 1
        })

    @classmethod
    def prepare_kta_payload(cls, member: dict, host_url: str) -> dict:
        """
        Prepares all metadata, dates, QR codes, and styling
        required to render the magnificent KTA.
        """
        nomor_induk = str(member.get('NOMOR INDUK', '')).strip()
        sabuk = str(member.get('SABUK', 'HIJAU')).strip().upper()
        belt_info = cls.get_belt_info(sabuk)

        # Verification URL
        clean_host = host_url.rstrip('/')
        verification_url = f"{clean_host}/verify/{nomor_induk}"

        # Generate Scannable QR Code base64 data URI
        qr_code_base64 = QRGenerator.generate_base64(verification_url, box_size=8, border=2)

        # Determine date of inauguration for current belt level
        tanggal_sah = member.get(sabuk)
        if not tanggal_sah or str(tanggal_sah).strip() == '':
            # Fallback to Hijau or Tanggal Sah
            tanggal_sah = member.get('HIJAU') or member.get('TANGGAL') or '25/05/2025'

        # Format TTL and Address
        ttl = str(member.get('TEMPAT TANGGAL LAHIR', '-')).strip()
        cabang = str(member.get('CABANG', 'PUSAT')).strip()
        status_kta = str(member.get('KTA', 'BELUM')).strip().upper()

        return {
            'member': member,
            'nomor_induk': nomor_induk,
            'nama_lengkap': str(member.get('NAMA LENGKAP', '')).strip().upper(),
            'sabuk': sabuk,
            'belt_info': belt_info,
            'cabang': cabang,
            'tanggal_sah': str(tanggal_sah).strip(),
            'ttl': ttl,
            'jenis_kelamin': str(member.get('JENIS KELAMIN', '-')).strip(),
            'verification_url': verification_url,
            'qr_code_base64': qr_code_base64,
            'is_physical_printed': status_kta == 'PUNYA',
            'status_kta': status_kta,
            'photo_url': member.get('FOTO_URL') or '/static/img/avatar_placeholder.svg',
        }

    @classmethod
    def generate_server_png(cls, member: dict, host_url: str, side: str = 'front') -> io.BytesIO:
        """
        Server-side high-resolution PNG image generation (1012x638 px, ID-1 300 DPI standard).
        """
        payload = cls.prepare_kta_payload(member, host_url)
        width, height = 1012, 638
        img = Image.new("RGB", (width, height), color=(14, 18, 24))
        draw = ImageDraw.Draw(img)

        # Try to load standard fonts, fallback to default
        try:
            font_title = ImageFont.truetype("arialbd.ttf", 26)
            font_subtitle = ImageFont.truetype("arial.ttf", 16)
            font_name = ImageFont.truetype("arialbd.ttf", 32)
            font_id = ImageFont.truetype("courbd.ttf", 24)
            font_label = ImageFont.truetype("arial.ttf", 14)
            font_val = ImageFont.truetype("arialbd.ttf", 16)
            font_belt = ImageFont.truetype("arialbd.ttf", 18)
            font_micro = ImageFont.truetype("arial.ttf", 11)
        except Exception:
            font_title = ImageFont.load_default()
            font_subtitle = font_title
            font_name = font_title
            font_id = font_title
            font_label = font_title
            font_val = font_title
            font_belt = font_title
            font_micro = font_title

        gold_primary = (212, 175, 55)
        gold_light = (245, 215, 127)
        green_dark = (14, 61, 19)
        white = (255, 255, 255)
        text_dim = (180, 180, 180)

        if side == 'front':
            # Background Luxury Gradient Lines / Accents
            for y in range(0, height, 4):
                alpha = int(14 + (y / height) * 10)
                draw.line([(0, y), (width, y)], fill=(alpha, alpha + 4, alpha + 8))

            # Gold Ornate Outer Border (Double Line)
            draw.rounded_rectangle([(14, 14), (width - 14, height - 14)], radius=24, outline=gold_primary, width=3)
            draw.rounded_rectangle([(22, 22), (width - 22, height - 22)], radius=18, outline=(140, 100, 20), width=1)

            # Top Header Bar (Deep Green Banner)
            draw.rounded_rectangle([(26, 26), (width - 26, 96)], radius=14, fill=green_dark, outline=gold_primary, width=1)

            # Header Titles
            draw.text((45, 34), "PERGURUAN SILAT BUANA NURRAGA", fill=gold_light, font=font_title)
            draw.text((45, 68), "KARTU TANDA ANGGOTA RESMI  •  OFFICIAL NATIONAL CREDENTIAL", fill=white, font=font_subtitle)

            # Photo Container on Left
            photo_rect = [(45, 120), (250, 385)]
            draw.rounded_rectangle(photo_rect, radius=12, fill=(24, 30, 40), outline=gold_primary, width=3)
            draw.text((95, 230), "[ FOTO ]", fill=gold_light, font=font_val)

            # Belt Ribbon below Photo
            draw.rounded_rectangle([(45, 395), (250, 435)], radius=8, fill=(46, 125, 50), outline=gold_light, width=1)
            draw.text((60, 403), payload['belt_info']['label'], fill=white, font=font_belt)

            # Anggota Identity Block (Center)
            draw.text((285, 120), "NAMA LENGKAP:", fill=gold_light, font=font_label)
            draw.text((285, 142), payload['nama_lengkap'], fill=white, font=font_name)

            # Nomor Induk Box
            draw.rounded_rectangle([(285, 190), (680, 235)], radius=8, fill=(28, 20, 10), outline=gold_primary, width=2)
            draw.text((300, 198), f"NO. INDUK : {payload['nomor_induk']}", fill=gold_light, font=font_id)

            # Data Grid
            draw.text((285, 255), "TINGKATAN :", fill=gold_primary, font=font_label)
            draw.text((400, 255), payload['belt_info']['level_name'], fill=white, font=font_val)

            draw.text((285, 290), "CABANG :", fill=gold_primary, font=font_label)
            draw.text((400, 290), payload['cabang'], fill=white, font=font_val)

            draw.text((285, 325), "TANGGAL SAH :", fill=gold_primary, font=font_label)
            draw.text((400, 325), payload['tanggal_sah'], fill=white, font=font_val)

            draw.text((285, 360), "STATUS :", fill=gold_primary, font=font_label)
            draw.text((400, 360), "ANGGOTA RESMI & AKTIF", fill=(76, 175, 80), font=font_val)

            # Right Side: QR Code Frame
            qr_frame = [(735, 120), (965, 350)]
            draw.rounded_rectangle(qr_frame, radius=12, fill=(255, 255, 255), outline=gold_primary, width=3)
            
            # Draw real QR image
            try:
                qr_pil = QRGenerator.generate_pil_image(payload['verification_url'], box_size=5, border=1)
                qr_pil = qr_pil.resize((210, 210))
                img.paste(qr_pil, (745, 130))
            except Exception:
                pass

            draw.text((755, 360), "PINDAI UNTUK VERIFIKASI", fill=gold_light, font=font_micro)

            # Footer Security Bar
            draw.rounded_rectangle([(26, height - 60), (width - 26, height - 26)], radius=10, fill=(18, 22, 28), outline=(100, 80, 20), width=1)
            draw.text((45, height - 48), "DEWAN PIMPINAN PUSAT BUANA NURRAGA  •  NUSA TENGGARA BARAT  •  DOKUMEN KEANGGOTAAN SAH", fill=text_dim, font=font_micro)

        else: # Sisi Belakang (Back)
            draw.rounded_rectangle([(14, 14), (width - 14, height - 14)], radius=24, outline=gold_primary, width=3)
            # Gold Magnetic Stripe
            draw.rectangle([(22, 40), (width - 22, 120)], fill=(35, 28, 15), outline=gold_primary, width=1)
            draw.text((45, 68), "BUANA NURRAGA SECURITY STRIPE  ••••  ENCRYPTED CREDENTIAL ARCHIVE", fill=gold_light, font=font_subtitle)

            # Rules / Ketentuan KTA
            draw.text((50, 145), "KETENTUAN KARTU TANDA ANGGOTA (KTA):", fill=gold_primary, font=font_val)
            rules = [
                "1. Kartu ini merupakan bukti keanggotaan sah Perguruan Silat Buana Nurraga.",
                "2. Wajib dibawa saat latihan resmi, ujian kenaikan tingkat (khataman), dan perhelatan perguruan.",
                "3. Pemegang kartu wajib menjunjung tinggi sumpah dan nama baik Perguruan Silat Buana Nurraga.",
                "4. Kartu ini tidak dapat dipindahtangankan kepada pihak manapun.",
                "5. Apabila menemukan kartu ini, harap hubungi Sekretariat Cabang terdekat atau scan QR Code di sisi depan."
            ]
            y_rule = 180
            for r in rules:
                draw.text((50, y_rule), r, fill=white, font=font_label)
                y_rule += 26

            # Sumpah Pendekar
            draw.rounded_rectangle([(50, 325), (width - 50, 410)], radius=10, fill=(20, 30, 22), outline=gold_primary, width=1)
            draw.text((65, 335), "IKRAR PENDEKAR BUANA NURRAGA:", fill=gold_light, font=font_val)
            draw.text((65, 360), "\"Bertaqwa kepada Tuhan Yang Maha Esa, Berbakti kepada Orang Tua dan Guru,", fill=white, font=font_label)
            draw.text((65, 382), "Berbudi Pekerti Luhur, Serta Mengamalkan Ilmu untuk Membela Kebenaran dan Keadilan.\"", fill=white, font=font_label)

            # Signature Blocks
            draw.text((120, 445), "Ketua Umum", fill=gold_light, font=font_label)
            draw.line([(80, 520), (240, 520)], fill=gold_primary, width=1)
            draw.text((85, 528), "( Pengurus Pusat )", fill=text_dim, font=font_micro)

            draw.text((width - 260, 445), "Guru Besar / Dewan Guru", fill=gold_light, font=font_label)
            draw.line([(width - 300, 520), (width - 140, 520)], fill=gold_primary, width=1)
            draw.text((width - 280, 528), "( Dewan Pendekar )", fill=text_dim, font=font_micro)

            # Bottom Center
            draw.text((width // 2 - 130, height - 45), "SEKRETARIAT PUSAT: NUSA TENGGARA BARAT", fill=text_dim, font=font_micro)

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer
