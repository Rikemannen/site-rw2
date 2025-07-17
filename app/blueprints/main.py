"""Handles main application routes and views."""

from flask import Blueprint, abort, render_template, request, redirect
from flask_login import current_user, login_required
from app.services.exercise_service import get_popular_exercises, get_recent_exercises, get_all_exercises
from app.services.user_service import get_user_by_id, get_all_users
from app.services.search_service import (
    search_users,
    search_users_by_id_partial,
    search_exercises,
    search_exercises_by_id_partial
)

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Render the index page."""
    return render_template('index.html',
                           popular_exercises=get_popular_exercises(),
                           recent_exercises=get_recent_exercises(), show_chat_window=False)

@bp.route('/user/<user_id>')
def user_profile(user_id):
    """Render the user profile page."""
    user = get_user_by_id(user_id)
    if not user:
        abort(404)
    return render_template('user/profile.html', user=user)

@bp.route('/profile')
@login_required
def profile():
    """Render the current user's profile page."""
    return redirect(f'/user/{current_user.id}')

@bp.route('/search')
def search():
    """Render the search results page."""
    query = request.args.get('q', '').strip()
    search_type = request.args.get('type', 'all')

    user_results = []
    exercise_results = []

    if query and query != "*":
        if search_type in ('all', 'users'):
            user_results.extend(search_users(query))
            if query.isdigit():
                id_results = search_users_by_id_partial(query)
                existing_ids = {user.id for user in user_results}
                user_results.extend(user for user in id_results if user.id not in existing_ids)

        if search_type in ('all', 'exercises'):
            exercise_results.extend(search_exercises(query))
            if query.isdigit():
                id_results = search_exercises_by_id_partial(query)
                existing_ids = {user.id for user in id_results}
                exercise_results.extend(user for user in id_results if user.id not in existing_ids)
    elif query == "*":
        if search_type in ('all', 'users'):
            user_results.extend(get_all_users())

        if search_type in ('all', 'exercises'):
            exercise_results.extend(get_all_exercises())

    return render_template(
        'search/results.html',
        query=query,
        search_type=search_type,
        user_results=user_results,
        exercise_results=exercise_results
    )
