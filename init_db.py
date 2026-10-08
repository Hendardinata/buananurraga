from app import create_app
from app.extensions import db
from app.models.user import User

app = create_app()

def seed_db():
    with app.app_context():
        print("Creating tables...")
        db.create_all()
        
        # Check if users exist
        if User.query.first() is None:
            print("Seeding initial users...")
            
            users = [
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
            
            for user_data in users:
                user = User(
                    username=user_data['username'],
                    full_name=user_data['full_name'],
                    role=user_data['role'],
                    branch_code=user_data['branch_code']
                )
                user.set_password(user_data['password'])
                db.session.add(user)
                
            db.session.commit()
            print("Users seeded successfully.")
        else:
            print("Database already contains users. Skipping seed.")

if __name__ == '__main__':
    seed_db()
