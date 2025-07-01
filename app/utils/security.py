from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

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