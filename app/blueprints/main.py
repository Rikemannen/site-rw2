"""Handles main application routes and views."""

from flask import Blueprint, abort, render_template, request, redirect
from flask_login import current_user, login_required
from app.models.emblems import Emblem
from app.services.emblem_service import get_emblem_by_id
from app.services.exercise_service import get_popular_exercises, get_recent_exercises, get_all_exercises
from app.services.user_service import get_user_by_id, get_all_users
from app.services.search_service import (
    search_users,
    search_users_by_id_partial,
    search_users_by_display_name,
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
    return render_template('user/profile.html', user=user, show_edit_links_user=True)

@bp.route('/profile')
@login_required
def profile():
    """Render the current user's profile page."""
    return redirect(f'/user/{current_user.id}')

@bp.route('/search')
def search():
    """Render the search results page."""
    query = request.args.get('q', '*').strip()
    search_type = request.args.get('type', 'all')

    user_results = []
    exercise_results = []

    if query and query != "*":
        if search_type in ('all', 'users'):
            user_results.extend(search_users(query))
            existing_ids = {user.id for user in user_results}
            user_results.extend(user for user in search_users_by_display_name(query) if user.id not in existing_ids)
            if query.isdigit():
                id_results = search_users_by_id_partial(query)
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

@bp.route('/emblems')
def emblems():
    """Render the page to show all emblems."""
    emblems = Emblem.query.all()
    return render_template('emblems.html', emblems=emblems)

@bp.route('/emblem/<int:emblem_id>')
def emblem_detail(emblem_id):
    """Render the detail page for a specific emblem."""
    emblem = get_emblem_by_id(emblem_id)
    if not emblem:
        abort(404)
    return render_template('emblem/detail.html', emblem=emblem)