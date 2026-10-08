from app.models.achievement import Achievement
from app.extensions import db

class AchievementService:
    @staticmethod
    def get_achievements_by_nomor_induk(nomor_induk):
        achievements = Achievement.query.filter_by(nomor_induk=str(nomor_induk).strip()).order_by(Achievement.tahun.desc()).all()
        return [ach.to_dict() for ach in achievements]

    @staticmethod
    def add_achievement(nomor_induk, data, username):
        new_ach = Achievement(
            nomor_induk=str(nomor_induk).strip(),
            nama_kejuaraan=data.get('nama_kejuaraan'),
            kategori=data.get('kategori'),
            tingkat=data.get('tingkat'),
            medali=data.get('medali'),
            tahun=int(data.get('tahun')),
            created_by=username
        )
        db.session.add(new_ach)
        db.session.commit()
        return new_ach

    @staticmethod
    def get_all_achievements():
        achievements = Achievement.query.order_by(Achievement.tahun.desc()).all()
        return [ach.to_dict() for ach in achievements]

    @staticmethod
    def delete_achievement(ach_id):
        ach = Achievement.query.get(ach_id)
        if ach:
            db.session.delete(ach)
            db.session.commit()
            return True
        return False
