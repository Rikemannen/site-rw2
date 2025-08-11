"""Handles user authentication routes and views."""

import time
import re
from urllib.parse import urlparse, urljoin
from datetime import datetime
from flask import Blueprint, flash, redirect, request, render_template, url_for, abort, json
from flask_login import current_user, login_required
from app.services.user_service import get_user_by_username, create_user, get_user_by_id, delete_user
from app.services.token_service import get_token_by_secret, invalidate_token
from app.services.session_token_service import login_user, logout_user, invalidate_all_sessions
from app.utils.security import verify_password, hash_password
from app.forms.auth_forms import LoginForm, SignupForm, RecoveryForm
from app.forms.settings_forms import ProfileSettingsForm, UsernameChangeForm, PasswordChangeForm, DeleteUserForm
from app.extensions import db
from app.services.logging_service import log

bp = Blueprint('auth', __name__)
pattern = r'^[a-zA-Z0-9]{1,20}$'

def is_safe_url(target):
    host_url = urlparse(request.host_url)
    redirect_url = urlparse(urljoin(request.host_url, target))
    return redirect_url.scheme in ('http', 'https') and host_url.netloc == redirect_url.netloc

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = get_user_by_username(form.username.data)
        if not user or not verify_password(user.password_hash, form.password.data):
            flash('Ogiltigt användarnamn eller lösenord.')
            return redirect(url_for('auth.login'))

        if user.banned:
            flash(f'Detta konto är bannlyst tills {datetime.fromtimestamp(user.banned_until).strftime('%Y-%m-%d %H:%M:%S')}!')
            return redirect(url_for('auth.login'))

        current_user.last_login = time.time()
        current_user.listed = True
        db.session.commit()
        next_url = request.form.get('next')
        if not next_url or not is_safe_url(next_url):
            next_url = url_for('main.index')

        resp = login_user(user)
        resp.headers['Location'] = next_url
        return resp

    return render_template('auth/login.html', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    form = SignupForm()
    if form.validate_on_submit():
        password = hash_password(form.password.data)

        if get_user_by_username(form.username.data):
            flash('Användarnamnet taget, använd ett annat!')
            return redirect(url_for('auth.register'))
        
        if re.match(pattern, form.username.data) is not None:
            pass
        else:
            flash('Användarnamnet får bara inehålla bokstäver och siffror, och vara 3-20 tecken!')
            return redirect(url_for('auth.register'))

        user = create_user(
            username=form.username.data,
            display_name=form.display_name.data or None,
            password_hash=password
        )

        if user:
            resp = login_user(user)
            return resp
        else:
            flash('Registreringen misslyckades, försök igen!')
            return redirect(url_for('auth.register'))
    return render_template('auth/register.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    resp = logout_user()
    return resp

@bp.route('/settings/profile', methods=['GET', 'POST'])
@login_required
def profile_settings():
    """Handle profile settings."""
    form = ProfileSettingsForm()

    form.emblem.choices = [(0, 'None')] + [(e.id, e.name) for e in current_user.emblems]

    if request.method == 'GET':
        form.display_name.data = current_user.display_name
        form.emblem.data = current_user.equipped_emblem_id
        form.description.data = current_user.description

    if form.validate_on_submit():
        current_user.display_name = form.display_name.data
        current_user.equipped_emblem_id = form.emblem.data
        desc = form.description.data.replace("\r\n", "\n").strip()
        desc = re.sub(r'\n{2,}', '\n\n', desc)
        desc = re.sub(r' {2,}', ' ', desc)
        current_user.description = desc

        if form.emblem.data == 0:
            current_user.equipped_emblem_id = None
        else:
            current_user.equipped_emblem_id = form.emblem.data

        db.session.commit()
        flash('Inställningarna har uppdaterats!', 'success')
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
    """Handle nameForm submissions"""
    nameForm = UsernameChangeForm()

    if nameForm.validate_on_submit():
        now = time.time()
        if (
            current_user.name_last_change is None
            or current_user.name_last_change + 14 * 86400 <= now
        ):
            if re.match(pattern, nameForm.username.data) is not None:
                current_user.name = nameForm.username.data
                current_user.name_last_change = now
                db.session.commit()
                flash('Användarnamnet har ändrats!')
            else:
                flash('Användarnamnet får bara inehålla bokstäver och siffror, och vara max 20 tecken!')
        else:
            flash('Du måste vänta 14 dagar innan du ändrar ditt namn igen.')
    return redirect(url_for('auth.account_settings'))

@bp.route('/settings/account/password', methods=['POST'])
@login_required
def password_change():
    passForm = PasswordChangeForm()

    if passForm.validate_on_submit():
        if not passForm.new_password.data == passForm.confirm_password.data:
            flash('Lösenorden matchar inte!')
        if verify_password(current_user.password_hash, passForm.current_password.data):
            current_user.password_hash = hash_password(passForm.new_password.data)
            db.session.commit()
            flash('Lösenordet har ändrats!')
    return redirect(url_for('auth.account_settings'))

@bp.route('/settings/account/delete', methods=['POST'])
@login_required
def account_deletion():
    deleteForm = DeleteUserForm()

    if deleteForm.validate_on_submit():
        if not deleteForm.username.data == current_user.name or not verify_password(current_user.password_hash, deleteForm.password.data) or not deleteForm.confirm.data:
            flash('Felaktig information!')
            return redirect(url_for('auth.account_settings'))

        delete_user(current_user, full=deleteForm.full.data)
    return redirect(url_for('main.index'))

@bp.route('/settings')
def settings_redirect():
    """Redirects /settings to /settings/profile"""
    return redirect(url_for('auth.profile_settings'))

@bp.route('/recover/<secret>', methods=['GET', 'POST'])
def recovery(secret):
    """Recover accounts using token."""
    recoveryForm = RecoveryForm()
    token = get_token_by_secret(secret)
    if not token or not token.is_valid:
        abort(403)
    user = get_user_by_id(token.user_id)
    
    if recoveryForm.validate_on_submit():
        user.password_hash = hash_password(recoveryForm.new_password.data)
        db.session.commit()
        invalidate_token(token)
        log(None, 'user', token.user_id, 'recovery.token_used', new_data=json.dumps({'token_id': token.id, 'token': token.secret[:10] + '...'}))
        return redirect(url_for('auth.login'))

    return render_template('auth/recovery.html', form=recoveryForm, recover=user)

@bp.route('/settings/account/signout', methods=['POST'])
@login_required
def logout_everywhere():
    invalidate_all_sessions(current_user)
    return redirect(url_for('main.index'))
