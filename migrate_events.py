from app import create_app
from app.extensions import db
from app.models.event import Event

app = create_app()

with app.app_context():
    db.create_all()
    print("1. Tabel events berhasil dipastikan ada di database.")

    if Event.query.count() == 0:
        event1 = Event(
            title="Kejuaraan Silat Antar Cabang Buana Nurraga Cup II 2026",
            category="Kejuaraan Resmi",
            description="Ajang silaturahmi akbar dan kejuaraan resmi pencak silat antar sasana dan cabang se-Nusa Tenggara Barat. Mempertandingkan kategori usia dini, remaja, dan dewasa seni dan tanding.",
            event_date="28 - 30 November 2026",
            location="Padepokan Utama Buana Nurraga, Lombok",
            organizer="Pengurus Pusat Perguruan Silat Buana Nurraga",
            poster_url="/static/uploads/events/poster_sample_cup2.jpg",
            registration_link="https://api.whatsapp.com/send?phone=6281234567890&text=Halo%20Panitia%20Buana%20Nurraga%20Cup%20II,%20saya%20ingin%20mendaftar%20kejuaraan.",
            status="UPCOMING",
            is_active=True,
            created_by="admin_pusat"
        )
        event2 = Event(
            title="Ujian Kenaikan Tingkat (UKT) dan Pendadaran Pendekar Akbar",
            category="Ujian Kenaikan Tingkat",
            description="Evaluasi penguasaan jurus, tata gerak tradisi, ketahanan fisik, dan keluhuran budi pekerti untuk kenaikan sabuk Hijau, Kuning, Merah, hingga persiapan Warga Hitam.",
            event_date="14 - 15 Desember 2026",
            location="Sentra Padepokan Tradisi, Lombok Tengah",
            organizer="Dewan Guru dan Pengurus Pusat Buana Nurraga",
            poster_url="/static/uploads/events/poster_sample_ukt.jpg",
            registration_link="https://api.whatsapp.com/send?phone=6281234567890&text=Halo%20Admin%20Pusat,%20saya%20ingin%20konfirmasi%20pendaftaran%20UKT%20Akbar.",
            status="UPCOMING",
            is_active=True,
            created_by="admin_pusat"
        )
        db.session.add(event1)
        db.session.add(event2)
        db.session.commit()
        print("2. Dua agenda event default berhasil ditambahkan.")
    else:
        print(f"2. Database sudah memiliki {Event.query.count()} event.")

    print("Selesai! Silakan reload web app di PythonAnywhere.")
