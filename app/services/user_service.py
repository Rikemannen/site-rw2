import sqlalchemy.exc
from app.extensions import db
from app.models.user import User
from app.services.exercise_service import delete_exercise
from app.services.chat_message_service import clear_user_messages

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
        password_hash=password_hash
    )
    db.session.add(user)
    try:
        db.session.commit()
        return user
    except sqlalchemy.exc.IntegrityError:
        db.session.rollback()
        return None

def get_all_users(c=None):
    """Returns a list with every user object."""
    return User.query.filter_by(listed=True).limit(c).all()

def delete_user(user, full=False):
    """Delete a user and all their traces."""
    if full:
        for exercise in user.exercises:
            delete_exercise(exercise)

        for session in user.sessions:
            db.session.delete(session)

        for token in user.tokens:
            db.session.delete(token)
        from app.services.message_service import delete_all_sent_messages
        delete_all_sent_messages(user)
        clear_user_messages(user)

        db.session.delete(user)
        try:
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            db.session.rollback()
    else:
        for session in user.sessions:
            session.valid = False
        for token in user.tokens:
            token.valid = False
        user.display_name = None
        user.name = "AVAKTIVERAD_" + str(user.id)
        user.description = "Användarens konto är avaktiverat!"
        user.equipped_emblem_id = None
        user.admin = False
        user.password_hash = ""
        user.listed = False
        try:
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            db.session.rollback()
