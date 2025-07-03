"""Handles exercise-related routes and views."""

import os
from flask import Blueprint, render_template, url_for, redirect
from flask_login import current_user as user
from app.services.exercise_service import get_exercise_by_id, increment_attempts, liked, unliked

bp = Blueprint('exercise', __name__, url_prefix='/exercise')

@bp.route('/<exercise_id>')
def view(exercise_id):
    """Render the exercise page."""
    exercise = get_exercise_by_id(exercise_id)
    if not exercise or not exercise.approved:
        return render_template('404.html'), 404
    return render_template(f'exercises/exercise.html', exercise=exercise)

@bp.route('/<exercise_id>/settings')
def settings(exercise_id):
    """Render the exercise settings page."""
    exercise = get_exercise_by_id(exercise_id)
    if not exercise or not user.owns_exercise(exercise):
        return render_template('403.html'), 403

    return render_template('exercise_settings.html', exercise=exercise)

@bp.route('/<exercise_id>/likes')
def likes(exercise_id):
    """Shows who has liked the exercise."""
    exercise = get_exercise_by_id(exercise_id)
    if not exercise or not exercise.approved:
        return render_template('404.html'), 404

    return render_template('exercises/likes.html', exercise=exercise)

@bp.route('/<exercise_id>/like', methods=['POST'])
def like(exercise_id):
    """Makes a user like an exercise. Unlikes if already liked."""
    exercise = get_exercise_by_id(exercise_id)
    if not exercise or not exercise.approved:
        return redirect(url_for('exercise.view', exercise_id=exercise.id)), 404

    if user.has_liked_exercise(exercise):
        unliked(user, exercise)
    else:
        liked(user, exercise)

    return redirect(url_for('exercise.view', exercise_id=exercise.id))

@bp.route('/<exercise_id>/submit')
def submit(exercise_id):
    exercise = get_exercise_by_id(exercise_id)