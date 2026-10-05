from werkzeug.security import generate_password_hash, check_password_hash

class UsersRepo:
    def __init__(self):
        # In-memory dictionary to hold user data (will be replaced by DB later)
        self.users = {
            'superadmin': {
                'username': 'superadmin',
                'password_hash': generate_password_hash('password123'),  # Default pass
                'full_name': 'Dewan Guru',
                'role': 'super_admin',
                'branch_code': None,
                'status': 'ACTIVE'
            },
            'admin_pusat': {
                'username': 'admin_pusat',
                'password_hash': generate_password_hash('password123'),
                'full_name': 'Sekretariat Pusat',
                'role': 'admin_pusat',
                'branch_code': None,
                'status': 'ACTIVE'
            },
            'admin_lotim': {
                'username': 'admin_lotim',
                'password_hash': generate_password_hash('password123'),
                'full_name': 'Admin Lombok Timur',
                'role': 'admin_cabang',
                'branch_code': 'LOTIM',
                'status': 'ACTIVE'
            },
            'admin_loteng': {
                'username': 'admin_loteng',
                'password_hash': generate_password_hash('password123'),
                'full_name': 'Admin Lombok Tengah',
                'role': 'admin_cabang',
                'branch_code': 'LOTENG',
                'status': 'ACTIVE'
            }
        }

    def get_user_by_username(self, username):
        return self.users.get(username)

    def verify_password(self, username, password):
        user = self.get_user_by_username(username)
        if user and check_password_hash(user['password_hash'], password):
            return True
        return False

# Global instance for now
users_repo = UsersRepo()
