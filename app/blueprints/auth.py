"""Handles user authentication routes and views."""

from flask import Blueprint, flash, redirect, request, render_template, url_for
import flask
from flask_login import login_user, current_user, login_required
#from werkzeug.urls import url_has_allowed_host_and_scheme
from app.services.user_service import get_user_by_username, create_user
from app.utils.security import verify_password, hash_password
from app.forms.auth_forms import LoginForm, SignupForm, SettingsForm
from app.extensions import db

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    form = LoginForm()
    if form.validate_on_submit():
        user = get_user_by_username(form.username.data)
        if not user or not verify_password(form.password.data, user.password_hash):
            flash('Invalid username or password.')
            return redirect(flask.url_for('auth.login'))

        login_user(user)

        flash('Login successful!')

        next_url = request.args.get('next')
        # TODO: Fix url validation check!
        #if not url_has_allowed_host_and_scheme(next_url, request.host):
        #    return flask.abort(400)
        return redirect(next_url or flask.url_for('main.index'))
    return render_template('auth/login.html', form=form)

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handle user signup."""
    form = SignupForm()
    if form.validate_on_submit():
        password = hash_password(form.password.data)

        user = create_user(
            username=form.username.data,
            password_hash=password
        )

        if user:
            login_user(user)
            flash('Signup successful! Welcome!')
            return redirect(flask.url_for('main.index'))
        else:
            flash('Signup failed. Please try again.')
    return render_template('auth/signup.html', form=form)

@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Handle user settings."""
    form = SettingsForm()

    # Populate emblem choices dynamically
    form.emblem.choices = [(e.id, e.name) for e in current_user.emblems]

    if request.method == 'GET':
        form.username.data = current_user.username
        form.display_name.data = current_user.display_name
        form.emblem.data = current_user.equipped_emblem_id
        # add other fields like description here if needed

    if form.validate_on_submit():
        if current_user.username != form.username.data:
            current_user.username = form.username.data
            # Optionally check username uniqueness here

        current_user.display_name = form.display_name.data
        current_user.equipped_emblem_id = form.emblem.data

        if form.password.data:
            current_user.password_hash = hash_password(form.password.data)

        db.session.commit()
        flash('Settings updated successfully.', 'success')
        return redirect(url_for('auth.settings'))

    return render_template('auth/settings.html', form=form)
