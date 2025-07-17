"""Handles user authentication routes and views."""

from flask import Blueprint, flash, redirect, request, render_template, url_for
import flask
import datetime
from flask_login import login_user, current_user, login_required, logout_user
from app.services.user_service import get_user_by_username, create_user
from app.utils.security import verify_password, hash_password
from app.forms.auth_forms import LoginForm, SignupForm
from app.forms.settings_forms import ProfileSettingsForm, UsernameChangeForm, PasswordChangeForm, DeleteUserForm
from app.extensions import db

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if current_user.is_authenticated:
        return redirect(flask.url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = get_user_by_username(form.username.data)
        if not user or not verify_password(user.password_hash, form.password.data):
            flash('Invalid username or password.')
            return redirect(flask.url_for('auth.login'))

        login_user(user)

        flash('Login successful!')

        next_url = request.form.get('next')

        if next_url:
            return redirect(next_url)
        return redirect(url_for('main.index'))

    return render_template('auth/login.html', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    form = SignupForm()
    if form.validate_on_submit():
        password = hash_password(form.password.data)

        if user_exists := get_user_by_username(form.username.data):
            flash('Användarnamnet taget, använd ett annat!')
            return redirect(flask.url_for('auth.register'))
        
        user = create_user(
            username=form.username.data,
            display_name=form.display_name.data or None,
            password_hash=password
        )

        if user:
            login_user(user)
            flash('Registration successful! Welcome!')
            return redirect(flask.url_for('main.index'))
        else:
            flash('Registration failed. Please try again.')
    return render_template('auth/register.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    flash('You have been logged out.')
    return redirect(flask.url_for('main.index'))

@bp.route('/settings/profile', methods=['GET', 'POST'])
@login_required
def profile_settings():
    """Handle profile settings."""
    form = ProfileSettingsForm()

    form.emblem.choices = [(0, 'None')] + [(e.id, e.name) for e in current_user.emblems]

    if request.method == 'GET':
        form.display_name.data = current_user.display_name
        form.emblem.data = current_user.equipped_emblem_id

    if form.validate_on_submit():
        current_user.display_name = form.display_name.data
        current_user.equipped_emblem_id = form.emblem.data

        if form.emblem.data == 0:
            current_user.equipped_emblem_id = None
        else:
            current_user.equipped_emblem_id = form.emblem.data

        db.session.commit()
        flash('Settings updated successfully.', 'success')
        return redirect(url_for('auth.profile_settings'))

    return render_template('auth/profile_settings.html', form=form)

@bp.route('/settings/account', methods=['GET', 'POST'])
@login_required
def account_settings():
    """Handle settings to username, password and account deletion."""
    nameForm = UsernameChangeForm()
    passForm = PasswordChangeForm()
    deleteForm = DeleteUserForm()

    if request.method == 'GET':
        nameForm.username.data = current_user.name

    return render_template(
        'auth/account_settings.html',
        nameForm=nameForm,
        passForm=passForm,
        deleteForm=deleteForm
    )

@bp.route('/settings/account/username', methods=['POST'])
@login_required
def username_change():
    nameForm = UsernameChangeForm()

    if nameForm.validate_on_submit():
        now = datetime.datetime.now(datetime.timezone.utc)
        if current_user.name_last_change is None or current_user.name_last_change + datetime.timedelta(days=14) <= now:
            current_user.name = nameForm.username.data
            current_user.name_last_change = now
            db.session.commit()
            flash('Användarnamnet har ändrats!')
            return redirect(url_for('auth.account_settings'))
        else:
            flash('Du måste vänta 14 dagar innan du ändrar ditt namn igen.')
            return redirect(url_for('auth.account_settings'))

@bp.route('/settings/account/password', methods=['POST'])
@login_required
def password_change():
    passForm = PasswordChangeForm()

    if passForm.validate_on_submit():
        if not passForm.new_password.data == passForm.confirm_password.data:
            flash('Passwords do not match!')
            return redirect(url_for('auth.account_settings'))
        if verify_password(current_user.password_hash, passForm.current_password.data):
            current_user.password_hash = hash_password(passForm.new_password.data)
            db.session.commit()
            flash('Lösenordet har ändrats!')
            return redirect(url_for('auth.account_settings'))
    return redirect(url_for('auth.account_settings'))

@bp.route('/settings/account/delete', methods=['POST'])
@login_required
def account_deletion():
    deleteForm = DeleteUserForm()

    if deleteForm.validate_on_submit():
        if not deleteForm.username.data == current_user.name or not verify_password(current_user.password_hash, deleteForm.password.data) or not deleteForm.confirm.data:
            flash('Felaktig information!')
            return redirect(url_for('auth.account_settings'))

        db.session.delete(current_user)
        db.session.commit()
        flash('Kontot har tagits bort :(')
        return redirect(url_for('main.index'))

@bp.route('/settings')
def settings_redirect():
    """Redirects /settings to /settings/profile"""
    return redirect(url_for('auth.profile_settings'))
