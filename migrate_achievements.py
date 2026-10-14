import sqlite3

conn = sqlite3.connect('../BN/app.db')
c = conn.cursor()

c.execute('PRAGMA table_info(achievements);')
cols = [col[1] for col in c.fetchall()]
print('Current columns in achievements:', cols)

if 'photo_url' not in cols:
    c.execute('ALTER TABLE achievements ADD COLUMN photo_url VARCHAR(512);')
    print('Added photo_url column to achievements table.')
else:
    print('photo_url column already exists.')

c.execute("UPDATE achievements SET photo_url = '/static/uploads/achievements/prestasi_sample_kejurda.jpg' WHERE photo_url IS NULL OR photo_url = '';")
conn.commit()

c.execute('SELECT id, nomor_induk, nama_kejuaraan, medali, photo_url FROM achievements;')
rows = c.fetchall()
for r in rows:
    print('Row in achievements:', r)

conn.close()
print('Migration complete!')
