from app.extensions import db
from app.models.exercise import Exercise
from app.services.file_service import create_exercise_files, delete_exercise_files

def get_exercise_by_id(exercise_id):
    """Retrieve exercise data based on its ID."""
    return db.session.query(Exercise).filter_by(id=exercise_id).first()

def get_exercise_by_name(name):
    """Retrieve exercise data based on its name."""
    return db.session.query(Exercise).filter_by(name=name).first()

def create_exercise(name, owner, html_data, json_data, description=None):
    """Create a new exercise with the given name and optional description."""
    exercise = Exercise(name=name, owner=owner, description=description)
    db.session.add(exercise)
    db.session.commit()
    create_exercise_files(exercise.id, html_data, json_data)
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
    return db.session.query(Exercise).order_by(Exercise.likes.desc()).limit(amount).all()

def get_recent_exercises(amount=3):
    """Retrieve the most recently created exercises."""
    return db.session.query(Exercise).order_by(Exercise.id.desc()).limit(amount).all()

def increment_attempts(exercise_id):
    """Increment the attempt count for a specific exercise."""
    exercise = get_exercise_by_id(exercise_id)
    if exercise:
        exercise.attempts += 1
        db.session.commit()
    else:
        raise ValueError(f"Exercise with ID {exercise_id} does not exist.")

def increment_finishes(exercise_id):
    """Increment the finish count for a specific exercise."""
    exercise = get_exercise_by_id(exercise_id)
    if exercise:
        exercise.finishes += 1
        db.session.commit()
    else:
        raise ValueError(f"Exercise with ID {exercise_id} does not exist.")

def increment_likes(exercise_id):
    """Increment the like count for a specific exercise."""
    exercise = get_exercise_by_id(exercise_id)
    if exercise:
        exercise.likes += 1
        db.session.commit()
    else:
        raise ValueError(f"Exercise with ID {exercise_id} does not exist.")