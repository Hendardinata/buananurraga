import os
from app import create_app
from app.extensions import db
from app.models.gallery import GalleryPost

app = create_app()

with app.app_context():
    # 1. Pastikan tabel terbuat di database
    db.create_all()
    print("1. Tabel gallery_posts berhasil dipastikan ada di database.")

    # 2. Pastikan folder penyimpanan upload foto ada
    upload_dir = os.path.join(app.root_path, 'static', 'uploads', 'instagram')
    os.makedirs(upload_dir, exist_ok=True)
    print(f"2. Direktori upload dipastikan siap: {upload_dir}")

    # 3. Seed data dokumentasi jika masih kosong
    if GalleryPost.query.count() == 0:
        posts_data = [
            {
                'title': 'Kontingen Buana Nurraga Raih Podium di Sumpah Pemuda Championship',
                'category': 'Kejuaraan',
                'category_slug': 'kejuaraan',
                'image_url': '/static/uploads/instagram/post1_sumpah_pemuda.jpg',
                'post_date': '28 Oktober 2025',
                'location': 'Gelanggang Pemuda Kota Mataram',
                'likes': 428,
                'comments': 56,
                'caption': 'Alhamdulillah! Prestasi membanggakan ditorehkan para ksatria muda Buana Nurraga pada ajang Sumpah Pemuda Championship. Kerja keras latihan fisik dan teknik berbuah manis di podium juara.\n\nTetap rendah hati, jaga sportivitas, dan terus mengasah diri untuk mengharumkan nama perguruan!\n\n#BuanaNurraga #SumpahPemudaChampionship #PencakSilatMataram #PendekarJuara #IPSI #SilatNusantara',
                'instagram_url': 'https://www.instagram.com/buananurraga/'
            },
            {
                'title': 'Tensi Tinggi & Ketenangan Jiwa di Mataram Cup II',
                'category': 'Kejuaraan',
                'category_slug': 'kejuaraan',
                'image_url': '/static/uploads/instagram/post2_mataram_cup.jpg',
                'post_date': '15 November 2025',
                'location': 'GOR 17 Desember Mataram',
                'likes': 382,
                'comments': 41,
                'caption': 'Aksi sengit atlet tanding Buana Nurraga di babak final Kejuaraan Pencak Silat Mataram Cup II. Setiap bantingan, pukulan, dan tendangan dieksekusi dengan ketenangan jiwa kesatria.\n\nKemenangan sejati adalah saat kita mampu mengendalikan diri sendiri di atas gelanggang.\n\n#BuanaNurraga #MataramCup #KejuaraanSilat #PesilatTangguh #IPSI_NTB #BelaDiriTradisi',
                'instagram_url': 'https://www.instagram.com/buananurraga/'
            },
            {
                'title': 'Latihan Gabungan Alam Terbuka di Sintung Park',
                'category': 'Latihan Gabungan',
                'category_slug': 'latihan',
                'image_url': '/static/uploads/instagram/post3_sintung_park.jpg',
                'post_date': '07 Desember 2025',
                'location': 'Sintung Park, Lombok Tengah',
                'likes': 512,
                'comments': 67,
                'caption': 'Menyatu dengan alam, memperkuat pondasi raga dan sukma. Sesi latihan gabungan seluruh cabang se-Lombok di kawasan asri Sintung Park.\n\nUdara segar pegunungan mengiringi gemuruh kekompakan jurus serempak ratusan pesilat Buana Nurraga.\n\n#BuanaNurraga #SintungPark #LatihanGabungan #PencakSilatAlam #LombokSilat #KeluargaBesar',
                'instagram_url': 'https://www.instagram.com/buananurraga/'
            },
            {
                'title': 'Malam Khidmat Pengesahan Warga Baru Perguruan',
                'category': 'Tradisi',
                'category_slug': 'tradisi',
                'image_url': '/static/uploads/instagram/post4_pengesahan_warga.jpg',
                'post_date': '27 Januari 2026',
                'location': 'Padepokan Pusat, Mataram NTB',
                'likes': 624,
                'comments': 89,
                'caption': 'Momen sakral dan penuh haru: Pengesahan Warga Baru Perguruan Silat Buana Nurraga. Ikrar janji setia pendekar telah diucapkan di hadapan para sesepuh dan dewan guru.\n\nBukan tentang seberapa kuat pukulanmu, melainkan seberapa teguh akhlakmu menjaga nama baik perguruan dan membela kebenaran.\n\n#BuanaNurraga #PengesahanWarga #MalamSakral #SumpahPendekar #BudiLuhur #TradisiNusantara',
                'instagram_url': 'https://www.instagram.com/buananurraga/'
            },
            {
                'title': 'Ujian Kenaikan Tingkat (UKT) & Evaluasi Sabuk',
                'category': 'Ujian Kenaikan Tingkat',
                'category_slug': 'ukt',
                'image_url': '/static/uploads/instagram/post5_ukt_sabuk.jpg',
                'post_date': '18 Februari 2026',
                'location': 'Sasana Diklat Buana Nurraga Pusat',
                'likes': 445,
                'comments': 53,
                'caption': 'Keringat dan dedikasi berbulan-bulan terbayar tuntas! Selamat kepada seluruh pesilat yang telah lulus evaluasi materi jurus, ketahanan fisik, dan mental dalam Ujian Kenaikan Tingkat (UKT).\n\nSabuk baru adalah tanggung jawab baru, bukan untuk menyombongkan diri melainkan pengingat untuk semakin merunduk.\n\n#BuanaNurraga #UKTSilat #KenaikanTingkat #UjianSabuk #PendekarMuda #DisiplinPendekar',
                'instagram_url': 'https://www.instagram.com/buananurraga/'
            },
            {
                'title': 'Silaturahmi Akbar Dewan Guru & Pendekar Nusantara',
                'category': 'Tradisi',
                'category_slug': 'tradisi',
                'image_url': '/static/uploads/instagram/post6_silaturahmi_akbar.jpg',
                'post_date': '02 Maret 2026',
                'location': 'Bale Pertemuan Buana Nurraga',
                'likes': 589,
                'comments': 64,
                'caption': 'Menjaga tali persaudaraan tanpa sekat. Silaturahmi Akbar mempertemukan para dewan guru, pelatih cabang, dan alumni atlet lintas angkatan Buana Nurraga.\n\nGuyub rukun, bersatu padu melestarikan warisan leluhur bangsa demi kejayaan pencak silat Indonesia.\n\n#BuanaNurraga #SilaturahmiAkbar #PersaudaraanSilat #SesepuhSilat #RukunKeluarga #BudayaNusantara',
                'instagram_url': 'https://www.instagram.com/buananurraga/'
            },
            {
                'title': 'Harmoni & Ketegasan Jurus Seni Tunggal Baku IPSI',
                'category': 'Kejuaraan',
                'category_slug': 'kejuaraan',
                'image_url': '/static/uploads/instagram/post7_seni_tunggal.jpg',
                'post_date': '22 Maret 2026',
                'location': 'Gelanggang Prestasi Silat NTB',
                'likes': 476,
                'comments': 38,
                'caption': 'Harmoni antara kelembutan rasa dan ketajaman teknik. Penampilan jurus seni tunggal baku pesilat putri Buana Nurraga memukau dewan juri dengan kemantapan gerak dan ekspresi kesatria.\n\nSeni adalah jiwa dari pencak silat.\n\n#BuanaNurraga #SeniTunggalIPSI #JurusBaku #SilatArt #PesilatPutri #PrestasiSeni',
                'instagram_url': 'https://www.instagram.com/buananurraga/'
            },
            {
                'title': 'Pembinaan Usia Dini & Latihan Perdana Cabang Lombok',
                'category': 'Latihan Gabungan',
                'category_slug': 'latihan',
                'image_url': '/static/uploads/instagram/post8_latihan_junior.jpg',
                'post_date': '05 April 2026',
                'location': 'Sasana Terbuka Lombok Timur',
                'likes': 398,
                'comments': 45,
                'caption': 'Mencetak bibit unggul sejak dini. Semangat membara adik-adik pesilat cilik Buana Nurraga pada latihan perdana ekspansi cabang Lombok Timur.\n\nTanamkan disiplin, rasa percaya diri, dan cinta tanah air melalui bela diri asli nusantara!\n\n#BuanaNurraga #SilatCilik #PembinaanUsiaDini #LombokTimur #BibitPendekar #GenerasiPenerus',
                'instagram_url': 'https://www.instagram.com/buananurraga/'
            }
        ]

        for idx, p in enumerate(posts_data):
            post_obj = GalleryPost(
                title=p['title'],
                category=p['category'],
                category_slug=p['category_slug'],
                image_url=p['image_url'],
                post_date=p['post_date'],
                location=p['location'],
                likes=p['likes'],
                comments=p['comments'],
                caption=p['caption'],
                instagram_url=p['instagram_url'],
                order_num=idx + 1,
                is_active=True,
                created_by='superadmin'
            )
            db.session.add(post_obj)
        db.session.commit()
        print(f"3. {len(posts_data)} foto dokumentasi awal berhasil disinkronkan ke database.")
    else:
        print(f"3. Database sudah memiliki {GalleryPost.query.count()} foto dokumentasi.")

    print("Selesai! Galeri & feed Instagram siap dikelola dari dashboard admin.")
