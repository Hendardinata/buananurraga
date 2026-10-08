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

    @staticmethod
    def format_date_display(val: str) -> str:
        if not val or not str(val).strip() or str(val).strip() == '-':
            return '-'
        val_str = str(val).strip()
        months_id = ["", "JANUARI", "FEBRUARI", "MARET", "APRIL", "MEI", "JUNI", "JULI", "AGUSTUS", "SEPTEMBER", "OKTOBER", "NOVEMBER", "DESEMBER"]
        try:
            if 'T' in val_str:
                clean_dt = val_str.replace('Z', '+00:00')
                from datetime import datetime
                dt = datetime.fromisoformat(clean_dt)
                return f"{dt.day:02d} {months_id[dt.month]} {dt.year}"
            elif '-' in val_str and len(val_str.split('-')) == 3:
                parts = val_str.split('-')
                if len(parts[0]) == 4:
                    from datetime import datetime
                    dt = datetime.strptime(val_str[:10], "%Y-%m-%d")
                    return f"{dt.day:02d} {months_id[dt.month]} {dt.year}"
            elif '/' in val_str:
                parts = val_str.split('/')
                if len(parts) == 3:
                    day = int(parts[0])
                    month = int(parts[1])
                    year = int(parts[2])
                    if 1 <= month <= 12:
                        return f"{day:02d} {months_id[month]} {year}"
        except Exception:
            pass
        return val_str

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
        formatted_tanggal_sah = cls.format_date_display(tanggal_sah)

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
            'tanggal_sah': formatted_tanggal_sah,
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
        Clean White Base, with Red, Black, and Green accents matching Perguruan Silat Buana Nurraga logo.
        """
        payload = cls.prepare_kta_payload(member, host_url)
        width, height = 1012, 638
        # Clean Pure White Card Base
        img = Image.new("RGB", (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)

        # Helper font loader with multiple fallbacks
        def load_font(font_names, size):
            for fname in font_names:
                try:
                    return ImageFont.truetype(fname, size)
                except Exception:
                    continue
            return ImageFont.load_default()

        font_super = load_font(["arialbd.ttf", "segoeuib.ttf"], 13)
        font_title = load_font(["georgiab.ttf", "arialbd.ttf", "segoeuib.ttf"], 25)
        font_subtitle = load_font(["arialbd.ttf", "segoeuib.ttf"], 14)
        font_name = load_font(["arialbd.ttf", "segoeuib.ttf"], 28)
        font_id = load_font(["courbd.ttf", "arialbd.ttf"], 21)
        font_label = load_font(["arial.ttf", "segoeui.ttf"], 13)
        font_val = load_font(["arialbd.ttf", "segoeuib.ttf"], 16)
        font_belt = load_font(["arialbd.ttf", "segoeuib.ttf"], 15)
        font_micro = load_font(["arial.ttf", "segoeui.ttf"], 12)
        font_badge = load_font(["arialbd.ttf", "segoeuib.ttf"], 13)

        # Brand Color Palette (Harmonized with Logo)
        c_black = (15, 23, 42)           # Slate-900: Deep Black
        c_black_deep = (0, 0, 0)
        c_red = (220, 38, 38)            # Crimson Red
        c_red_dark = (153, 27, 27)       # Deep Red
        c_green = (21, 128, 61)          # Forest Green
        c_green_emerald = (22, 163, 74)  # Emerald Green
        c_slate = (71, 85, 105)          # Slate-600
        c_muted = (100, 116, 139)        # Slate-500
        c_border_light = (226, 232, 240) # Slate-200
        c_white = (255, 255, 255)

        # Draw subtle anti-counterfeit guilloche wave lines across card
        for y_wave in range(30, height - 30, 28):
            draw.line([(30, y_wave), (width - 30, y_wave)], fill=(244, 247, 250), width=1)
        for x_wave in range(30, width - 30, 32):
            draw.line([(x_wave, 30), (x_wave, height - 30)], fill=(248, 250, 252), width=1)

        if side == 'front':
            # Outer Sharp Black Border (Standard ID-1 Outer Frame)
            draw.rounded_rectangle([(14, 14), (width - 14, height - 14)], radius=24, outline=c_black, width=3)
            # Inner Subtle Security Border
            draw.rounded_rectangle([(20, 20), (width - 20, height - 20)], radius=18, outline=c_border_light, width=1)



            # Paste Official Logo
            logo_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'img', 'logo.png')
            if os.path.exists(logo_path):
                try:
                    logo_img = Image.open(logo_path).convert("RGBA")
                    logo_img = logo_img.resize((76, 76), Image.Resampling.LANCZOS)
                    img.paste(logo_img, (40, 25), mask=logo_img)
                except Exception:
                    pass

            # Header Brand Text
            def draw_centered_text(cx, y, txt, font_obj, color):
                if hasattr(font_obj, 'getbbox'):
                    w = font_obj.getbbox(txt)[2] - font_obj.getbbox(txt)[0]
                elif hasattr(font_obj, 'getsize'):
                    w = font_obj.getsize(txt)[0]
                else:
                    w = font_obj.getlength(txt) if hasattr(font_obj, 'getlength') else len(txt) * 8
                draw.text((cx - (w / 2), y), txt, fill=color, font=font_obj)

            header_cx = (130 + (width - 40)) // 2
            draw_centered_text(header_cx, 26, "DEWAN PIMPINAN PUSAT • NUSA TENGGARA BARAT", font_super, c_green)
            draw_centered_text(header_cx, 46, "PERGURUAN SILAT BUANA NURRAGA", font_title, c_black)
            draw_centered_text(header_cx, 78, "KARTU TANDA ANGGOTA RESMI • OFFICIAL NATIONAL CREDENTIAL", font_subtitle, c_red)



            # Tricolor Brand Stripe below Header (Red - Black - Green)
            stripe_y = 104
            draw.line([(130, stripe_y), (370, stripe_y)], fill=c_red, width=2)
            draw.line([(370, stripe_y), (670, stripe_y)], fill=c_black, width=2)
            draw.line([(670, stripe_y), (width - 40, stripe_y)], fill=c_green_emerald, width=2)

            # Photo Container on Left
            photo_rect = [(42, 120), (245, 375)]
            draw.rounded_rectangle(photo_rect, radius=10, fill=(248, 250, 252), outline=c_black, width=2)
            draw.rounded_rectangle([(46, 124), (241, 371)], radius=8, outline=c_red, width=1)

            # Try to load real member photo, otherwise draw clean avatar silhouette
            photo_loaded = False
            raw_photo_url = payload.get('photo_url', '')
            if raw_photo_url and not raw_photo_url.endswith('.svg'):
                if raw_photo_url.startswith('/static/'):
                    local_p = os.path.join(os.path.dirname(__file__), '..', raw_photo_url.lstrip('/'))
                    if os.path.exists(local_p):
                        try:
                            m_photo = Image.open(local_p).convert("RGB")
                            m_photo = m_photo.resize((195, 247), Image.Resampling.LANCZOS)
                            img.paste(m_photo, (46, 124))
                            photo_loaded = True
                        except Exception:
                            pass

            if not photo_loaded:
                # Dignified clean placeholder portrait with Martial Arts collar
                draw.ellipse([(108, 160), (178, 230)], fill=(226, 232, 240), outline=c_slate, width=2)
                draw.polygon([(75, 335), (143, 260), (211, 335)], fill=(226, 232, 240), outline=c_slate)
                draw.text((105, 342), "FOTO RESMI", fill=c_muted, font=font_micro)

            # Smart Chip Graphic below Photo
            chip_box = [(42, 388), (115, 436)]
            draw.rounded_rectangle(chip_box, radius=6, fill=(245, 158, 11), outline=(180, 83, 9), width=1)
            # Chip internal contact pads
            draw.rectangle([(55, 396), (102, 428)], outline=(180, 83, 9), width=1)
            draw.line([(78, 396), (78, 428)], fill=(180, 83, 9), width=1)
            draw.line([(55, 412), (102, 412)], fill=(180, 83, 9), width=1)

            # Overlapping Red Official Stamp on photo corner
            stamp_cx, stamp_cy = 238, 362
            draw.circle((stamp_cx, stamp_cy), 22, fill=(255, 255, 255), outline=c_red, width=2)
            draw.circle((stamp_cx, stamp_cy), 18, outline=c_red, width=1)
            draw.text((stamp_cx - 10, stamp_cy - 8), "BN", fill=c_red_dark, font=font_micro)

            # Anggota Identity Block (Center)
            draw.text((275, 122), "NAMA LENGKAP ANGGOTA", fill=c_muted, font=font_label)
            draw.text((275, 142), payload['nama_lengkap'], fill=c_black, font=font_name)

            # Nomor Induk Box (Black Luxury Pill)
            draw.rounded_rectangle([(275, 186), (680, 232)], radius=8, fill=c_black, outline=c_red, width=1)
            draw.text((295, 196), f"NO. INDUK : {payload['nomor_induk']}", fill=c_white, font=font_id)

            # Data Grid
            draw.text((275, 252), "TINGKATAN", fill=c_muted, font=font_label)
            # Belt Ribbon Box
            belt_label = payload['belt_info']['label']
            belt_bg = c_green
            if 'BIRU' in belt_label:
                belt_bg = (13, 71, 161)
            elif 'COKELAT' in belt_label and 'HITAM' not in belt_label:
                belt_bg = (93, 64, 55)
            elif 'ORANGE' in belt_label:
                belt_bg = (230, 81, 0)
            elif 'GURU' in belt_label:
                belt_bg = (180, 83, 9)

            draw.rounded_rectangle([(390, 246), (660, 276)], radius=6, fill=belt_bg, outline=c_border_light, width=1)
            draw.text((404, 252), belt_label, fill=c_white, font=font_belt)

            draw.text((275, 290), "CABANG", fill=c_muted, font=font_label)
            draw.text((390, 290), payload['cabang'], fill=c_black, font=font_val)

            draw.text((275, 325), "TANGGAL SAH", fill=c_muted, font=font_label)
            draw.text((390, 325), payload['tanggal_sah'], fill=c_slate, font=font_val)

            draw.text((275, 360), "MASA BERLAKU", fill=c_muted, font=font_label)
            draw.text((390, 360), "SEUMUR HIDUP / AKTIF", fill=c_green, font=font_val)

            # Right Side: QR Code Frame (Shrunk and aligned right)
            qr_frame = [(785, 120), (965, 300)]
            draw.rounded_rectangle(qr_frame, radius=10, fill=c_white, outline=c_black, width=2)
            
            # Draw real QR image inside frame
            try:
                qr_pil = QRGenerator.generate_pil_image(payload['verification_url'], box_size=5, border=1)
                qr_pil = qr_pil.resize((160, 160))
                img.paste(qr_pil, (795, 130))
            except Exception:
                pass

            draw_centered_text(875, 310, "PINDAI UNTUK VERIFIKASI", font_micro, c_green)

            # Footer Security Bar
            draw.line([(40, height - 58), (width - 40, height - 58)], fill=c_border_light, width=1)
            draw.text((45, height - 46), "BUANA NURRAGA INDONESIA • KEABSAHAN TERCATAT PUSAT", fill=c_muted, font=font_micro)
            draw.text((width - 250, height - 46), f"SEC-ID: {payload['nomor_induk']}", fill=c_black, font=font_micro)

        else: # Sisi Belakang (Back)
            # Outer Sharp Black Border
            draw.rounded_rectangle([(14, 14), (width - 14, height - 14)], radius=24, outline=c_black, width=3)
            draw.rounded_rectangle([(20, 20), (width - 20, height - 20)], radius=18, outline=c_border_light, width=1)

            # Deep Black Magnetic Stripe with Security Text
            draw.rectangle([(20, 32), (width - 20, 108)], fill=(15, 23, 42))
            draw.text((45, 60), f"BN-CREDENTIAL-SECURITY-BAND  ••••  {payload['nomor_induk']}  ••••  ENCRYPTED ARCHIVE", fill=c_white, font=font_subtitle)

            # Rules / Ketentuan KTA
            draw.text((50, 136), "KETENTUAN PEMEGANG KARTU TANDA ANGGOTA (KTA):", fill=c_red_dark, font=font_val)
            rules = [
                "1. Kartu ini merupakan bukti keanggotaan sah Perguruan Silat Buana Nurraga.",
                "2. Wajib dibawa saat latihan resmi, ujian kenaikan tingkat (khataman), dan perhelatan perguruan.",
                "3. Pemegang kartu wajib menjunjung tinggi sumpah dan nama baik Perguruan Silat Buana Nurraga.",
                "4. Kartu ini tidak dapat dipindahtangankan kepada pihak manapun.",
                "5. Apabila menemukan kartu ini, harap hubungi Sekretariat Cabang terdekat atau scan QR Code di sisi depan."
            ]
            y_rule = 168
            for r in rules:
                draw.text((50, y_rule), r, fill=(30, 41, 59), font=font_label)
                y_rule += 24

            # Sumpah / Ikrar Pendekar Box
            ikrar_rect = [(50, 305), (width - 50, 395)]
            draw.rounded_rectangle(ikrar_rect, radius=8, fill=(240, 253, 244), outline=(187, 247, 208), width=1)
            # Left Green Accent Border
            draw.line([(50, 305), (50, 395)], fill=c_green_emerald, width=5)
            draw.text((68, 316), "IKRAR PENDEKAR BUANA NURRAGA:", fill=c_green, font=font_val)
            draw.text((68, 342), "\"Bertaqwa kepada Tuhan Yang Maha Esa, Berbakti kepada Orang Tua dan Guru,", fill=c_black, font=font_label)
            draw.text((68, 364), "Berbudi Pekerti Luhur, Serta Mengamalkan Ilmu untuk Membela Kebenaran dan Keadilan.\"", fill=c_black, font=font_label)

            # Signature Blocks
            draw.text((130, 428), "Ketua Umum", fill=c_black, font=font_val)
            draw.line([(70, 502), (250, 502)], fill=c_black, width=1)
            draw.text((95, 510), "( Pengurus Besar Pusat )", fill=c_muted, font=font_micro)

            draw.text((width - 280, 428), "Guru Besar / Dewan Guru", fill=c_black, font=font_val)
            draw.line([(width - 320, 502), (width - 120, 502)], fill=c_black, width=1)
            draw.text((width - 280, 510), "( Pimpinan Keilmuan )", fill=c_muted, font=font_micro)

            # Center Seal Simulation (Carmine Red Stamp matching seal_official)
            seal_cx, seal_cy = width // 2, 465
            draw.circle((seal_cx, seal_cy), 44, fill=(255, 255, 255), outline=c_red, width=2)
            draw.circle((seal_cx, seal_cy), 40, outline=c_red, width=1)
            draw.circle((seal_cx, seal_cy), 28, outline=c_red, width=1)
            draw.text((seal_cx - 28, seal_cy - 18), "CAP RESMI", fill=c_red, font=font_micro)
            draw.text((seal_cx - 12, seal_cy - 7), "BN", fill=c_red_dark, font=font_val)
            draw.text((seal_cx - 18, seal_cy + 8), "PUSAT", fill=c_red, font=font_micro)

            # Bottom Center Footer
            draw.line([(40, height - 52), (width - 40, height - 52)], fill=c_border_light, width=1)
            draw.text((50, height - 42), "SEKRETARIAT PUSAT: NUSA TENGGARA BARAT", fill=c_muted, font=font_micro)
            draw.text((width - 250, height - 42), "PORTAL: BUANANURRAGA.ORG", fill=c_muted, font=font_micro)

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer
