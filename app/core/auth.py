from functools import wraps
from flask import session, request, redirect, url_for, abort
from app.repositories.in_memory.users_repo import users_repo

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def role_required(allowed_roles):
    """
    Decorator for checking if the current user has the required role.
    allowed_roles: list of roles or a single role string.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('auth.login', next=request.url))
                
            user = users_repo.get_user_by_username(session['user_id'])
            if not user:
                session.clear()
                return redirect(url_for('auth.login'))
                
            roles = allowed_roles if isinstance(allowed_roles, list) else [allowed_roles]
            
            if user['role'] not in roles:
                abort(403) # Forbidden
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_current_user():
    if 'user_id' in session:
        return users_repo.get_user_by_username(session['user_id'])
    return None

def has_branch_access(branch_code):
    """
    Check if current user has access to a specific branch
    """
    user = get_current_user()
    if not user:
        return False
        
    if user['role'] in ['super_admin', 'admin_pusat']:
        return True
        
    return user['branch_code'] == branch_code
