from app.extensions import db
from app.models.user import User
from app.models.exercise import Exercise

def search_users(query):
    """Search for users based on usernames."""
    if not query:
        return []

    results = User.query.filter(User.name.ilike(f'%{query}%')).all()
    # Returns a list of user objects that match the query username,
    # has to later be linked to profile(s) via id
    return results

def search_users_by_id_partial(user_id):
    """Search for users whose IDs start with the given user_id."""
    if not user_id:
        return []

    # Convert user_id to string for partial matching
    user_id_str = str(user_id)
    results = User.query.filter(User.id.cast(db.String).like(f'{user_id_str}%')).all()
    # Returns users whose IDs start with the given digits
    return results

def search_users_by_display_name(display_name):
    """Search for users based on display names."""
    if not display_name:
        return []

    results = User.query.filter(User.display_name.ilike(f'%{display_name}%')).all()
    return results

def search_exercises(query):
    """Search for exercises based on names."""
    if not query:
        return []

    results = Exercise.query.filter(Exercise.approved).filter(Exercise.name.ilike(f'%{query}%')).all()
    # Returns a list of exercise objects that match the query name
    return results

def search_exercises_by_id_partial(exercise_id):
    """Search for users whose IDs start with the given user_id."""
    if not exercise_id:
        return []

    # Convert exercise_id to string for partial matching
    exercise_id_str = str(exercise_id)
    results = Exercise.query.filter(Exercise.approved).filter(Exercise.id.cast(db.String).like(f'{exercise_id_str}%')).all()
    # Returns exercises whose IDs start with the given digits
    return results