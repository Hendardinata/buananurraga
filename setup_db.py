from app import create_app
from app.extensions import db
from app.models.user import User

app = create_app()

with app.app_context():
    # 1. Buat semua tabel
    db.create_all()
    print("Tabel database berhasil dibuat!")

    # 2. Daftar user default
    default_users = [
        {
            'username': 'superadmin',
            'password': 'password123',
            'full_name': 'Dewan Guru',
            'role': 'super_admin',
            'branch_code': None
        },
        {
            'username': 'admin_pusat',
            'password': 'password123',
            'full_name': 'Sekretariat Pusat',
            'role': 'admin_pusat',
            'branch_code': None
        },
        {
            'username': 'admin_lotim',
            'password': 'password123',
            'full_name': 'Admin Lombok Timur',
            'role': 'admin_cabang',
            'branch_code': 'LOTIM'
        },
        {
            'username': 'admin_loteng',
            'password': 'password123',
            'full_name': 'Admin Lombok Tengah',
            'role': 'admin_cabang',
            'branch_code': 'LOTENG'
        }
    ]

    # 3. Masukkan ke database jika belum ada
    for user_data in default_users:
        user = User.query.filter_by(username=user_data['username']).first()
        if not user:
            new_user = User(
                username=user_data['username'],
                full_name=user_data['full_name'],
                role=user_data['role'],
                branch_code=user_data['branch_code']
            )
            new_user.set_password(user_data['password'])
            db.session.add(new_user)
            print(f"User '{user_data['username']}' berhasil ditambahkan.")
        else:
            print(f"User '{user_data['username']}' sudah ada, dilewati.")

    db.session.commit()
    print("Inisialisasi database selesai!")
