from sqlalchemy import func
from datetime import datetime, timezone
from app.extensions import db
from app.models.exercise import Exercise, exercise_likes
from app.services.file_service import create_exercise_files, delete_exercise_files

def get_exercise_by_id(exercise_id):
    """Retrieve exercise data based on its ID."""
    return Exercise.query.filter_by(id=exercise_id).first()

def get_exercise_by_name(name):
    """Retrieve exercise data based on its name."""
    return Exercise.query.filter_by(name=name).first()

def create_exercise(name, owner, html_data, json_data, description=None, approved=False):
    """Create a new exercise with the given name and optional description."""
    exercise = Exercise(name=name, owner=owner, description=description, approved=approved, created=int(datetime.now(timezone.utc).timestamp()))
    db.session.add(exercise)
    db.session.commit()
    create_exercise_files(exercise, html_data, json_data)
    return exercise

def delete_exercise(exercise_id):
    """Delete an exercise by its ID."""
    exercise = get_exercise_by_id(exercise_id)
    if exercise:
        db.session.delete(exercise)
        db.session.commit()
        delete_exercise_files(exercise_id)
    else:
        raise ValueError(f"Exercise with ID {exercise_id} does not exist.")

def update_exercise(exercise_id, name=None, description=None):
    """Update an existing exercise's name and/or description. (For users to update exercise data, they need to remove and reupload the exercise.)"""
    exercise = get_exercise_by_id(exercise_id)
    if not exercise:
        raise ValueError(f"Exercise with ID {exercise_id} does not exist.")
    
    if name:
        exercise.name = name
    if description:
        exercise.description = description
    
    db.session.commit()
    return exercise

def get_popular_exercises(amount=3):
    """Retrieve the most popular exercises based on the number of likes."""
    return (
        db.session.query(Exercise, func.count(exercise_likes.c.user_id).label('likes_count'))
        .outerjoin(exercise_likes, Exercise.id == exercise_likes.c.exercise_id)
        .filter(Exercise.approved)
        .group_by(Exercise.id)
        .order_by(func.count(exercise_likes.c.user_id).desc())
        .limit(amount)
        .all()
    )

def get_recent_exercises(amount=3):
    """Retrieve the most recently created exercises."""
    return Exercise.query.filter(Exercise.approved == True).order_by(Exercise.created.desc()).limit(amount).all()

def increment_attempts(exercise):
    """Increment the attempt count for a specific exercise."""
    if exercise:
        exercise.attempts += 1
        db.session.commit()
    else:
        raise ValueError(f"Exercise with ID {exercise.id} does not exist.")

def increment_finishes(exercise):
    """Increment the finish count for a specific exercise."""
    if exercise:
        exercise.finished += 1
        db.session.commit()
    else:
        raise ValueError(f"Exercise with ID {exercise.id} does not exist.")

def liked(user, exercise):
    """Add a user to the "liked users" of an exercise."""
    if exercise:
        exercise.liked_by.append(user)
        db.session.commit()
    else:
        raise ValueError(f"Exercise with ID {exercise.id} does not exist.")

def unliked(user, exercise):
    """Remove a user from the "liked users" of an exercise."""
    if exercise:
        if user in exercise.liked_by:
            exercise.liked_by.remove(user)
            db.session.commit()
        else:
            raise ValueError(f"User {user.name} has not liked exercise {exercise.id}.")
    else:
        raise ValueError(f"Exercise with ID {exercise.id} does not exist.")

def get_all_exercises():
    """Returns a list with every exercise object."""
    return Exercise.query.all()
