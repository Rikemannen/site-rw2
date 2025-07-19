from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from functools import wraps
from flask import abort
from flask_login import current_user

password_hasher = PasswordHasher()

def hash_password(password):
    """Hash a password using Argon2."""
    return password_hasher.hash(password)

def verify_password(hashed, password):
    """Verify a password against a hashed value."""
    try:
        password_hasher.verify(hashed, password)
        return True
    except VerifyMismatchError:
        return False

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function