"""Handles exercise-related routes and views."""

from flask import Blueprint, render_template
from flask_login import current_user as user
from app.services.exercise_service import get_exercise_by_id, increment_attempts

bp = Blueprint('exercises', __name__, url_prefix='/')

@bp.route('/exercise/<exercise_id>')
def view_exercise(exercise_id):
    """Render the exercise page."""
    exercise = get_exercise_by_id(exercise_id)
    if not exercise:
        return render_template('404.html'), 404
    increment_attempts(exercise_id)
    return render_template(f'app/exercises/{exercise_id}/exercise.html', exercise=exercise)

@bp.route('/exercise/<exercise_id>/settings')
def exercise_settings(exercise_id):
    """Render the exercise settings page."""
    exercise = get_exercise_by_id(exercise_id)
    if not exercise or not user.owns_exercise(exercise):
        return render_template('403.html'), 403

    return render_template('exercise_settings.html', exercise=exercise)

@bp.route('/exercise/<exercise_id>/likes')
def exercise_likes(exercise_id):
    """Shows who has liked the exercise.""" # TODO: Implement this properly
    exercise = get_exercise_by_id(exercise_id)
    if not exercise:
        return render_template('404.html'), 404

    return render_template('404.html'), 404 # Still wip ¯\_(ツ)_/¯
    return render_template('exercise_likes.html', exercise=exercise)