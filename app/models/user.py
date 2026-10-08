from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(64), nullable=False, default='admin_cabang')
    branch_code = db.Column(db.String(64), nullable=True) # Only for admin_cabang
    is_active = db.Column(db.Boolean, default=True)
    session_token = db.Column(db.String(256), nullable=True)
    last_active = db.Column(db.DateTime, nullable=True)

    def __init__(self, username, full_name, role='admin_cabang', branch_code=None, **kwargs):
        super(User, self).__init__(**kwargs)
        self.username = username
        self.full_name = full_name
        self.role = role
        self.branch_code = branch_code

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'role': self.role,
            'branch_code': self.branch_code,
            'is_active': self.is_active
        }
