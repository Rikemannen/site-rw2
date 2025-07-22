import sqlalchemy.exc
from datetime import datetime, timezone
from app.extensions import db
from app.models.user import User

def get_user_by_id(user_id):
    """Retrieve user data based on their ID."""
    return User.query.filter_by(id=user_id).first()

def get_user_by_username(username):
    """Retrieve user data based on their username."""
    return User.query.filter_by(name=username).first()

def user_exists(username):
    """Check if a user with the given username exists."""
    return User.query.filter_by(username=username).count() > 0

def create_user(username, display_name, password_hash):
    """Create a new user with the given username, display name, and password hash."""
    user = User(
        name=username,
        display_name=display_name,
        password_hash=password_hash,
        joined=int(datetime.now(timezone.utc).timestamp())
    )
    db.session.add(user)
    try:
        db.session.commit()
        return user
    except sqlalchemy.exc.IntegrityError:
        db.session.rollback()
        return None

def get_all_users():
    """Returns a list with every user object."""
    return User.query.all()
