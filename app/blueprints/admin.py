from flask import Blueprint, render_template, request, abort, redirect, url_for, flash
from flask_login import current_user as user
from app.utils.security import admin_required
from app.services.user_service import get_user_by_id
from app.services.token_service import generate_token, get_url
from app.models.emblems import Emblem
from app.extensions import db
from app.forms.admin_forms import (
    ProfileSettingsForm,
    EmblemAssignmentForm,
    UsernameChangeForm,
    PasswordResetForm,
    DeleteUserForm,
    VerifyUserForm,
    ElevateUserForm
)

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/')
@admin_required
def admin():
    """Render the base admin page."""
    return render_template('admin/admin.html')

@bp.route('/user/<user_id>')
@admin_required
def edit_user(user_id):
    """Handle user related stuff."""
    profileForm = ProfileSettingsForm()
    emblemForm = EmblemAssignmentForm()
    usernameForm = UsernameChangeForm()
    passwordForm = PasswordResetForm()
    deleteForm = DeleteUserForm()
    verifyForm = VerifyUserForm()
    elevateForm = ElevateUserForm()
    editing = get_user_by_id(user_id)

    if not editing:
        abort(404)

    profileForm.emblem.choices = [(0, 'None')] + [(e.id, e.name) for e in editing.emblems]
    emblemForm.emblems.choices = [(e.id, e.name) for e in Emblem.query.all()]
    emblemForm.emblems.data = [e.id for e in editing.emblems]
    print("data:",emblemForm.emblems.data,"owned:",editing.emblems)

    if request.method == 'GET':
        profileForm.display_name.data = editing.display_name
        profileForm.emblem.data = editing.equipped_emblem_id
        usernameForm.username.data = editing.name
        verifyForm.verified.data = editing.verified
        elevateForm.admin.data = editing.admin

    return render_template('admin/user.html', user=user, editing=editing,
                           profileForm=profileForm,
                           emblemForm=emblemForm,
                           nameForm=usernameForm,
                           passForm=passwordForm,
                           deleteForm=deleteForm,
                           verifyForm=verifyForm,
                           elevateForm=elevateForm
                           )

@bp.route('/user/<user_id>/profile', methods=['POST'])
@admin_required
def profile_editing(user_id):
    """Handle profileForm submission."""
    profileForm = ProfileSettingsForm()
    editing = get_user_by_id(user_id)
    profileForm.emblem.choices = [(0, 'None')] + [(e.id, e.name) for e in editing.emblems]
    if profileForm.validate_on_submit():
        editing.display_name = profileForm.display_name.data
        editing.equipped_emblem_id = profileForm.emblem.data if profileForm.emblem.data != 0 else None
        db.session.commit()
        return redirect(url_for('admin.edit_user', user_id=editing.id))
    return redirect(url_for('admin.admin'))

@bp.route('/user/<user_id>/emblems', methods=['POST'])
@admin_required
def emblems(user_id):
    """Handle emblemForm submission."""
    emblemForm = EmblemAssignmentForm()
    editing = get_user_by_id(user_id)

    emblemForm.emblems.choices = [(e.id, e.name) for e in Emblem.query.all()]
    print("received data:",emblemForm.emblems.data)
    if emblemForm.validate_on_submit():
        editing.emblems.clear()
        selected_ids = [int(e_id) for e_id in emblemForm.emblems.data]
        selected_emblems = Emblem.query.filter(Emblem.id.in_(selected_ids)).all()
        editing.emblems.extend(selected_emblems)
        db.session.commit()
        return redirect(url_for('admin.edit_user', user_id=editing.id))
    return redirect(url_for('admin.admin'))

@bp.route('/user/<user_id>/username', methods=['POST'])
@admin_required
def username_editing(user_id):
    """Handle usernameForm submission."""
    usernameForm = UsernameChangeForm()
    editing = get_user_by_id(user_id)

    if usernameForm.validate_on_submit():
        editing.name = usernameForm.username.data
        db.session.commit()
        return redirect(url_for('admin.edit_user', user_id=editing.id))
    return redirect(url_for('admin.admin'))

@bp.route('/user/<user_id>/recovery', methods=['POST'])
@admin_required
def recovery(user_id):
    """Handle resetForm submission."""
    resetForm = PasswordResetForm()
    editing = get_user_by_id(user_id)

    if resetForm.validate_on_submit():
        token = generate_token(editing)
        url = get_url(token, request.host)
        flash(url)
        return redirect(url_for('admin.edit_user', user_id=editing.id))
    return redirect(url_for('admin.admin'))

@bp.route('/user/<user_id>/delete', methods=['POST'])
@admin_required
def deletion(user_id):
    """Handle deleteForm submissions."""
    deleteForm = DeleteUserForm()
    editing = get_user_by_id(user_id)

    if deleteForm.validate_on_submit():
        db.session.delete(editing)
        db.session.commit()
        return redirect(url_for('admin.admin'))
    return redirect(url_for('admin.admin'))

@bp.route('/user/<user_id>/verify', methods=['POST'])
@admin_required
def verify(user_id):
    """Handle verfiyForm submissions."""
    verifyForm = VerifyUserForm()
    editing = get_user_by_id(user_id)

    if verifyForm.validate_on_submit():
        editing.verified = verifyForm.verified.data
        db.session.commit()
        return redirect(url_for('admin.edit_user', user_id=editing.id))
    return redirect(url_for('admin.admin'))

@bp.route('/user/<user_id>/elevate', methods=['POST'])
@admin_required
def elevate(user_id):
    """Handle elevateForm submissions."""
    elevateForm = ElevateUserForm()
    editing = get_user_by_id(user_id)

    if elevateForm.validate_on_submit():
        editing.admin = elevateForm.admin.data
        db.session.commit()
        return redirect(url_for('admin.edit_user', user_id=editing.id))
    return redirect(url_for('admin.admin'))
