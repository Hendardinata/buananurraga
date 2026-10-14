import os
import uuid
from datetime import datetime
from flask import current_app
from app.models.achievement import Achievement
from app.extensions import db

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

class AchievementService:
    @staticmethod
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @staticmethod
    def save_photo(file):
        """
        Simpan berkas foto prestasi / podium / medali ke app/static/uploads/achievements/
        Mengembalikan path URL publik seperti /static/uploads/achievements/ach_xxx.jpg
        """
        if not file or not file.filename:
            return None

        if not AchievementService.allowed_file(file.filename):
            return None

        ext = file.filename.rsplit('.', 1)[1].lower()
        now_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        rand_str = uuid.uuid4().hex[:8]
        unique_name = f"ach_{now_str}_{rand_str}.{ext}"

        upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'achievements')
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, unique_name)
        file.save(file_path)

        return f'/static/uploads/achievements/{unique_name}'

    @staticmethod
    def get_achievement_by_id(ach_id):
        return Achievement.query.get(ach_id)

    @staticmethod
    def get_achievements_by_nomor_induk(nomor_induk):
        achievements = Achievement.query.filter_by(nomor_induk=str(nomor_induk).strip()).order_by(Achievement.tahun.desc(), Achievement.id.desc()).all()
        return [ach.to_dict() for ach in achievements]

    @staticmethod
    def add_achievement(nomor_induk, data, username, photo_file=None):
        photo_url = None
        if photo_file and photo_file.filename:
            photo_url = AchievementService.save_photo(photo_file)

        if not photo_url and data.get('photo_url'):
            photo_url = data.get('photo_url').strip()

        new_ach = Achievement(
            nomor_induk=str(nomor_induk).strip(),
            nama_kejuaraan=data.get('nama_kejuaraan', '').strip(),
            kategori=data.get('kategori', '').strip(),
            tingkat=data.get('tingkat', 'Provinsi').strip(),
            medali=data.get('medali', 'Emas').strip(),
            tahun=int(data.get('tahun') or datetime.now().year),
            photo_url=photo_url,
            created_by=username
        )
        db.session.add(new_ach)
        db.session.commit()
        return new_ach

    @staticmethod
    def update_achievement(ach_id, data, photo_file=None):
        ach = Achievement.query.get(ach_id)
        if not ach:
            return None

        if photo_file and photo_file.filename:
            new_photo = AchievementService.save_photo(photo_file)
            if new_photo:
                # Hapus foto lama jika tersimpan lokal
                if ach.photo_url and ach.photo_url.startswith('/static/uploads/achievements/'):
                    try:
                        fname = os.path.basename(ach.photo_url)
                        old_p = os.path.join(current_app.root_path, 'static', 'uploads', 'achievements', fname)
                        if os.path.exists(old_p):
                            os.remove(old_p)
                    except Exception:
                        pass
                ach.photo_url = new_photo
        elif data.get('photo_url'):
            ach.photo_url = data.get('photo_url').strip()

        if data.get('nama_kejuaraan'):
            ach.nama_kejuaraan = data.get('nama_kejuaraan').strip()
        if data.get('kategori'):
            ach.kategori = data.get('kategori').strip()
        if data.get('tingkat'):
            ach.tingkat = data.get('tingkat').strip()
        if data.get('medali'):
            ach.medali = data.get('medali').strip()
        if data.get('tahun'):
            ach.tahun = int(data.get('tahun'))

        db.session.commit()
        return ach

    @staticmethod
    def get_all_achievements():
        achievements = Achievement.query.order_by(Achievement.tahun.desc(), Achievement.id.desc()).all()
        return [ach.to_dict() for ach in achievements]

    @staticmethod
    def delete_achievement(ach_id):
        ach = Achievement.query.get(ach_id)
        if ach:
            if ach.photo_url and ach.photo_url.startswith('/static/uploads/achievements/'):
                try:
                    fname = os.path.basename(ach.photo_url)
                    p = os.path.join(current_app.root_path, 'static', 'uploads', 'achievements', fname)
                    if os.path.exists(p):
                        os.remove(p)
                except Exception:
                    pass
            db.session.delete(ach)
            db.session.commit()
            return True
        return False
