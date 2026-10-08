from app.extensions import db
from datetime import datetime

class Achievement(db.Model):
    __tablename__ = 'achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    nomor_induk = db.Column(db.String(64), nullable=False, index=True)
    nama_kejuaraan = db.Column(db.String(256), nullable=False)
    kategori = db.Column(db.String(128), nullable=False)
    tingkat = db.Column(db.String(64), nullable=False) # e.g., Kabupaten, Provinsi, Nasional, Internasional
    medali = db.Column(db.String(32), nullable=False) # e.g., Emas, Perak, Perunggu
    tahun = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(64), nullable=True) # Username who created this record

    def __init__(self, nomor_induk, nama_kejuaraan, kategori, tingkat, medali, tahun, created_by=None, **kwargs):
        super(Achievement, self).__init__(**kwargs)
        self.nomor_induk = nomor_induk
        self.nama_kejuaraan = nama_kejuaraan
        self.kategori = kategori
        self.tingkat = tingkat
        self.medali = medali
        self.tahun = tahun
        self.created_by = created_by

    def to_dict(self):
        return {
            'id': self.id,
            'nomor_induk': self.nomor_induk,
            'nama_kejuaraan': self.nama_kejuaraan,
            'kategori': self.kategori,
            'tingkat': self.tingkat,
            'medali': self.medali,
            'tahun': self.tahun,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'created_by': self.created_by
        }
