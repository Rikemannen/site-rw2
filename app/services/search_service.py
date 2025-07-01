from app.extensions import db
from app.models.user import User
from app.models.exercise import Exercise

def search_users(query):
    """Search for users based on usernames."""
    if not query:
        return []

    results = db.session.query(User).filter(User.username.ilike(f'%{query}%')).all()
    # Returns a list of user objects that match the query username,
    # has to later be linked to profile(s) via id
    return results

def search_users_by_id_partial(user_id):
    """Search for users whose IDs start with the given user_id."""
    if not user_id:
        return []

    # Convert user_id to string for partial matching
    user_id_str = str(user_id)
    results = db.session.query(User).filter(User.id.cast(db.String).like(f'{user_id_str}%')).all()
    # Returns users whose IDs start with the given digits
    return results

# TODO: Implement display names

def search_users_by_display_name(display_name):
    pass

def search_exercises(query):
    """Search for exercises based on names."""
    if not query:
        return []

    results = db.session.query(Exercise).filter(Exercise.name.ilike(f'%{query}%')).all()
    # Returns a list of exercise objects that match the query name
    return results

def search_exercises_by_id_partial(exercise_id):
    """Search for users whose IDs start with the given user_id."""
    if not exercise_id:
        return []

    # Convert exercise_id to string for partial matching
    exercise_id_str = str(exercise_id)
    results = db.session.query(Exercise).filter(Exercise.id.cast(db.String).like(f'{exercise_id_str}%')).all()
    # Returns exercises whose IDs start with the given digits
    return results