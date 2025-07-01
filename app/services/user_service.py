from app.extensions import db
from app.models.user import User

def get_user_by_id(user_id):
    """Retrieve user data based on their ID."""
    return db.session.query(User).filter_by(id=user_id).first()

def get_user_by_username(username):
    """Retrieve user data based on their username."""
    return db.session.query(User).filter_by(username=username).first()

def create_user(username, password_hash):
    """Create a new user with the given username and password hash."""
    user = User(username=username, password_hash=password_hash)
    db.session.add(user)
    db.session.commit()
    return user