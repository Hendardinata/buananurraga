import os
import sqlite3
from app import create_app

app = create_app()

with app.app_context():
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if db_uri.startswith('sqlite:///'):
        db_path = db_uri.replace('sqlite:///', '')
        if not os.path.isabs(db_path):
            db_path = os.path.join(app.root_path, '..', db_path)
    else:
        db_path = os.path.join(os.path.dirname(__file__), 'app.db')

    db_path = os.path.abspath(db_path)
    print(f"Menggunakan database: {db_path}")

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute('PRAGMA table_info(achievements);')
    cols = [col[1] for col in c.fetchall()]
    print('Current columns in achievements:', cols)

    if 'photo_url' not in cols:
        c.execute('ALTER TABLE achievements ADD COLUMN photo_url VARCHAR(512);')
        print('1. Added photo_url column to achievements table.')
    else:
        print('1. photo_url column already exists.')

    c.execute("UPDATE achievements SET photo_url = '/static/uploads/achievements/prestasi_sample_kejurda.jpg' WHERE photo_url IS NULL OR photo_url = '';")
    conn.commit()

    c.execute('SELECT id, nomor_induk, nama_kejuaraan, medali, photo_url FROM achievements;')
    rows = c.fetchall()
    for r in rows:
        print('Row in achievements:', r)

    conn.close()
    print("Selesai! Kolom photo_url berhasil dipastikan dan disinkronkan.")
    print("Silakan reload web app di PythonAnywhere Web tab.")
