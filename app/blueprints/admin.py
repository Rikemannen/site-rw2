import ast
import re
import time
import sqlalchemy.exc
import json
from flask import Blueprint, render_template, request, abort, redirect, url_for, flash
from flask_login import current_user
from app.models.user import User
from app.models.exercise import Exercise
from app.utils.security import admin_required
from app.services.user_service import get_user_by_id, delete_user, get_all_users
from app.services.exercise_service import get_exercise_by_id
from app.services.token_service import generate_token, get_url, invalidate_token, get_token_by_id
from app.services.file_service import create_exercise_files, delete_exercise_files, get_exercise_html, get_exercise_answers
from app.services.emblem_service import get_emblem_by_id, create_emblem as createEmblem
from app.services.logging_service import log
from app.services.session_token_service import invalidate_all_sessions
from app.services.message_service import send_message_to_all
from app.services.chat_message_service import clear_user_messages as clear_user_msgs
from app.services.event_service import get_event, create_event, get_all_events, delete_event
from app.models.logs import Log
from app.models.emblems import Emblem
from app.models.token import Token
from app.models.session_tokens import SessionToken
from app.extensions import db, socketio
from app.forms.admin_forms import *

bp = Blueprint('admin', __name__, url_prefix='/admin')
HIDDEN_DATA = {'password_hash'}

@bp.route('/')
@admin_required
def admin():
    """Render the base admin page."""
    user_count = User.query.count()
    exercise_count = Exercise.query.count()
    latest_user = User.query.order_by(User.joined.desc()).first()
    total_attempts = db.session.query(db.func.sum(Exercise.attempts)).scalar() or 0
    total_completions = db.session.query(db.func.sum(Exercise.finished)).scalar() or 0
    sessions = SessionToken.query.count()
    valid_sessions = SessionToken.query.filter_by(valid=True).count()
    return render_template('admin/admin.html', user_count=user_count, exercise_count=exercise_count,
                           latest_user=latest_user, attempt_count=total_attempts,
                           completed_count=total_completions, sessions=sessions, valid_sessions=valid_sessions)

@bp.route('/logs')
@admin_required
def logs():
    """Render the logs page."""
    count = request.args.get('c', default=100, type=int)
    logs = db.session.query(Log).order_by(Log.id.desc()).limit(count).all()
    return render_template('admin/logs.html', logs=logs)

@bp.route('/tokens')
@admin_required
def tokens():
    """Show all tokens."""
    tokens = Token.query.order_by(Token.id.desc()).all()
    tokens.sort(key=lambda t: not t.is_valid)
    return render_template('admin/tokens.html', tokens=tokens)

@bp.route('/bans')
@admin_required
def bans():
    """Show all banned users."""
    banned_users = User.query.filter(User.banned_until > time.time()).all()
    return render_template('admin/bans.html', bans=banned_users)

# --- Event related routes within /admin. ---

@bp.route('/events', methods=['GET', 'POST'])
@admin_required
def manage_events():
    """Manage events."""
    events = get_all_events()
    form = EventCreationForm()

    if form.validate_on_submit():
        # Convert form.expires.data (a datetime object) to a Unix timestamp
        expires_ts = int(form.expires.data.timestamp())
        raw_data = form.event_data.data
        try:
            data = json.loads(raw_data) if raw_data else {}
        except json.JSONDecodeError:
            flash("Ogiltig json!")
            return redirect(url_for('admin.manage_events'))
        create_event(
            event_type=form.event_type.data,
            data=data,
            expires=expires_ts
        )
        return redirect(url_for('admin.manage_events'))

    return render_template('admin/events.html', events=events, form=form)

@bp.route('/events/<event_type>/delete', methods=['POST'])
@admin_required
def event_deletion(event_type):
    """Delete an event."""
    event = get_event(event_type)

    if not event:
        abort(404)

    delete_event(event)
    return redirect(url_for('admin.manage_events'))

# --- User related routes within /admin. ---

@bp.route('/user')
@admin_required
def users():
    """Render the user search page."""
    return redirect(url_for('main.search', q='*', type='users', c=-1))

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
    banForm = BanUserForm()
    unbanForm = UnbanUserForm()
    editing = get_user_by_id(user_id)

    if not editing:
        abort(404)

    user_data = {k: v for k, v in vars(editing).items() if not k.startswith('_') and k not in HIDDEN_DATA}

    profileForm.emblem.choices = [(0, 'None')] + [(e.id, e.name) for e in editing.emblems]
    emblemForm.emblems.choices = [(e.id, e.name) for e in Emblem.query.all()]
    emblemForm.emblems.data = [e.id for e in editing.emblems]

    if request.method == 'GET':
        profileForm.display_name.data = editing.display_name
        profileForm.emblem.data = editing.equipped_emblem_id
        profileForm.description.data = editing.description
        usernameForm.username.data = editing.name
        verifyForm.verified.data = editing.verified
        elevateForm.admin.data = editing.admin

    return render_template('admin/user.html', user=current_user, editing=editing, user_data=user_data,
                           profileForm=profileForm,
                           emblemForm=emblemForm,
                           nameForm=usernameForm,
                           passForm=passwordForm,
                           deleteForm=deleteForm,
                           verifyForm=verifyForm,
                           elevateForm=elevateForm,
                           unbanForm=unbanForm,
                           banForm=banForm
                           )

@bp.route('/user/<user_id>/profile', methods=['POST'])
@admin_required
def profile_editing(user_id):
    """Handle profileForm submission."""
    profileForm = ProfileSettingsForm()
    editing = get_user_by_id(user_id)

    if not editing:
        abort(404)

    profileForm.emblem.choices = [(0, 'None')] + [(e.id, e.name) for e in editing.emblems]
    if profileForm.validate_on_submit():
        editing.display_name = profileForm.display_name.data
        editing.equipped_emblem_id = profileForm.emblem.data if profileForm.emblem.data != 0 else None
        desc = profileForm.description.data.replace("\r\n", "\n").strip()
        desc = re.sub(r'\n{2,}', '\n\n', desc)
        desc = re.sub(r' {2,}', ' ', desc)
        editing.description = desc
        try:
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            db.session.rollback()
        return redirect(url_for('admin.edit_user', user_id=editing.id))
    return redirect(url_for('admin.admin'))

@bp.route('/user/<user_id>/emblems', methods=['POST'])
@admin_required
def emblems(user_id):
    """Handle emblemForm submission."""
    emblemForm = EmblemAssignmentForm()
    editing = get_user_by_id(user_id)

    if not editing:
        abort(404)

    emblemForm.emblems.choices = [(e.id, e.name) for e in Emblem.query.all()]
    if emblemForm.validate_on_submit():
        editing.emblems.clear()
        selected_ids = [int(e_id) for e_id in emblemForm.emblems.data]
        selected_emblems = Emblem.query.filter(Emblem.id.in_(selected_ids)).all()
        editing.emblems.extend(selected_emblems)
        try:
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            db.session.rollback()
        return redirect(url_for('admin.edit_user', user_id=editing.id))
    return redirect(url_for('admin.admin'))

@bp.route('/user/<user_id>/username', methods=['POST'])
@admin_required
def username_editing(user_id):
    """Handle usernameForm submission."""
    usernameForm = UsernameChangeForm()
    editing = get_user_by_id(user_id)

    if not editing:
        abort(404)

    if usernameForm.validate_on_submit():
        log(current_user, 'user', editing.id, 'name.change', old_data=editing.name, new_data=usernameForm.username.data)
        editing.name = usernameForm.username.data
        try:
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            db.session.rollback()
        return redirect(url_for('admin.edit_user', user_id=editing.id))
    return redirect(url_for('admin.admin'))

@bp.route('/user/<user_id>/recovery', methods=['POST'])
@admin_required
def recovery(user_id):
    """Handle resetForm submission."""
    resetForm = PasswordResetForm()
    editing = get_user_by_id(user_id)

    if not editing:
        abort(404)

    if resetForm.validate_on_submit():
        token = generate_token(editing, current_user)
        url = get_url(token, request.host)
        log(current_user, 'user', editing.id, 'recovery.token_generated', new_data=json.dumps({'id': token.id, 'token': token.secret[:10] + '...'}))
        log(current_user, 'token', token.id, 'created', new_data=json.dumps({'token': token.secret[:10] + '...', 'expires': token.expires}))
        flash(url)
        return redirect(url_for('admin.edit_user', user_id=editing.id, _anchor='link'))
    return redirect(url_for('admin.admin'))

@bp.route('/user/<user_id>/delete', methods=['POST'])
@admin_required
def deletion(user_id):
    """Handle deleteForm submissions."""
    deleteForm = DeleteUserForm()
    editing = get_user_by_id(user_id)

    if not editing:
        abort(404)

    if deleteForm.validate_on_submit():
        delete_user(editing, full=deleteForm.full.data)
        log(current_user, 'user', editing.id, 'delete', new_data=json.dumps({'full': deleteForm.full.data}))

    if deleteForm.full.data:
        return redirect(url_for('admin.admin'))
    return redirect(url_for('admin.edit_user', user_id=editing.id))

@bp.route('/user/<user_id>/verify', methods=['POST'])
@admin_required
def verify(user_id):
    """Handle verfiyForm submissions."""
    verifyForm = VerifyUserForm()
    editing = get_user_by_id(user_id)

    if not editing:
        abort(404)

    if verifyForm.validate_on_submit():
        editing.verified = verifyForm.verified.data
        try:
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            db.session.rollback()
        log(current_user, 'user', editing.id, 'verified.verify' if verifyForm.verified.data else 'verified.unverify')
        return redirect(url_for('admin.edit_user', user_id=editing.id))
    return redirect(url_for('admin.admin'))

@bp.route('/user/<user_id>/elevate', methods=['POST'])
@admin_required
def elevate(user_id):
    """Handle elevateForm submissions."""
    elevateForm = ElevateUserForm()
    editing = get_user_by_id(user_id)

    if not editing:
        abort(404)

    if elevateForm.validate_on_submit():
        editing.admin = elevateForm.admin.data
        try:
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            db.session.rollback()
        log(current_user, 'user', editing.id, 'admin.elevate' if elevateForm.admin.data else 'admin.demote')
        return redirect(url_for('admin.edit_user', user_id=editing.id))
    return redirect(url_for('admin.admin'))

@bp.route('/user/<user_id>/ban', methods=['POST'])
@admin_required
def ban(user_id):
    """Handle user access change (banForm, unbanForm)."""
    banForm = BanUserForm()
    editing = get_user_by_id(user_id)

    if banForm.validate_on_submit():
        invalidate_all_sessions(editing)
        editing.banned_until = time.time() + (int(banForm.time.data) * 24 * 60 * 60)
        try:
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            db.session.rollback()
    return redirect(url_for('admin.edit_user', user_id=editing.id))

@bp.route('/user/<user_id>/unban', methods=['POST'])
@admin_required
def unban(user_id):
    unbanForm = UnbanUserForm()
    editing = get_user_by_id(user_id)

    if unbanForm.validate_on_submit():
        editing.banned_until = 0
        try:
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            db.session.rollback()
    return redirect(url_for('admin.edit_user', user_id=editing.id))

@bp.route('/user/<user_id>/clear-messages', methods=['POST'])
@admin_required
def clear_user_messages(user_id):
    """Remove all messages from user."""
    user = get_user_by_id(user_id)
    clear_user_msgs(user)
    return redirect(url_for('admin.edit_user', user_id=user.id))

@bp.route('/message-all', methods=['GET', 'POST'])
@admin_required
def message_all():
    form = MessageAllForm()

    if form.validate_on_submit():
        content = form.content.data.replace("\r\n", "\n").strip()
        content = re.sub(r'\n{2,}', '\n\n', content)
        content = re.sub(r' {2,}', ' ', content)
        msg = send_message_to_all(sender=current_user, content=content)
        for user in get_all_users():
            entry = next((m for m in msg if m.recipient_id == user.id), None)
            socketio.emit(
            'new_message',
            {'id': entry.id, 'sender': current_user.name, 'content': content},
            room=str(user.id)
        )
        flash('Meddelandet har skickats!')
        return redirect(url_for('admin.message_all'))
    return render_template('admin/message.html', form=form)

# --- Exercise related routes within /admin. ---

@bp.route('/exercise')
@admin_required
def exercises():
    """Render the exercise search page."""
    return redirect(url_for('main.search', q='*', type='exercises'))

@bp.route('/exercise/preview/<exercise_id>')
@admin_required
def preview_exercise(exercise_id):
    """Allow admins to preview unapproved exercises."""
    exercise = get_exercise_by_id(exercise_id)
    if not exercise:
        abort(404)
    return render_template('exercises/exercise.html', exercise=exercise, show_edit_links=True)

@bp.route('/exercise/<exercise_id>')
@admin_required
def edit_exercise(exercise_id):
    infoForm = ExerciseInfoForm()
    dataForm = ExerciseDataForm()
    statisticForm = ExerciseStatisticForm()
    htmlForm = ExerciseHTMLForm()
    answerForm = ExerciseAnswerForm()
    deleteForm = DeleteExerciseForm()
    editing = get_exercise_by_id(exercise_id)

    if not editing:
        abort(404)

    exercise_data = {k: v for k, v in vars(editing).items() if not k.startswith('_')}

    json = get_exercise_answers(editing)
    html = get_exercise_html(editing)


    if request.method == 'GET':
        infoForm.name.data = editing.name
        infoForm.description.data = editing.description
        dataForm.owner.data = editing.owner_id
        dataForm.created.data = editing.created
        dataForm.approved.data = editing.approved
        statisticForm.attempts.data = editing.attempts
        statisticForm.completions.data = editing.finished
        answerForm.json.data = json
        htmlForm.html.data = html

    return render_template('admin/exercise.html', user=current_user, editing=editing, exercise_data=exercise_data,
                           basicForm=infoForm,
                           staticForm=dataForm,
                           statisticForm=statisticForm,
                           htmlForm=htmlForm,
                           answerForm=answerForm,
                           deleteForm=deleteForm)

@bp.route('/exercise/<id>/info', methods=['POST'])
@admin_required
def edit_info(id):
    infoForm = ExerciseInfoForm()
    editing = get_exercise_by_id(id)

    if not editing:
        abort(404)

    if infoForm.validate_on_submit():
        editing.name = infoForm.name.data
        desc = infoForm.description.data.replace("\r\n", "\n").strip()
        desc = re.sub(r'\n{2,}', '\n\n', desc)
        desc = re.sub(r' {2,}', ' ', desc)
        editing.description = desc
        try:
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            db.session.rollback()
        return redirect(url_for('admin.edit_exercise', exercise_id=editing.id))
    return redirect(url_for('admin.admin'))

@bp.route('/exercise/<id>/static', methods=['POST'])
@admin_required
def edit_static(id):
    dataForm = ExerciseDataForm()
    editing = get_exercise_by_id(id)

    if not editing:
        abort(404)

    if dataForm.validate_on_submit():
        if dataForm.approved.data != editing.approved:
            log(current_user, 'exercise', editing.id, 'approve' if dataForm.approved.data else 'unapprove')
        if dataForm.owner.data != editing.owner_id or dataForm.created.data != editing.created:
            log(current_user, 'exercise', editing.id, 'static.update', old_data=json.dumps({
                'owner_id': editing.owner_id,
                'created': editing.created
            }), new_data=json.dumps({
                'owner_id': dataForm.owner.data,
                'created': dataForm.created.data
            }))
        editing.owner_id = dataForm.owner.data
        editing.created = dataForm.created.data
        editing.approved = dataForm.approved.data
        try:
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            db.session.rollback()
        return redirect(url_for('admin.edit_exercise', exercise_id=editing.id))
    return redirect(url_for('admin.admin'))

@bp.route('/exercise/<id>/statistics', methods=['POST'])
@admin_required
def edit_stats(id):
    statisticForm = ExerciseStatisticForm()
    editing = get_exercise_by_id(id)

    if not editing:
        abort(404)

    if statisticForm.validate_on_submit():
        editing.attempts = statisticForm.attempts.data
        editing.finished = statisticForm.completions.data
        try:
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            db.session.rollback()
        return redirect(url_for('admin.edit_exercise', exercise_id=editing.id))
    return redirect(url_for('admin.admin'))

@bp.route('/exercise/<id>/json', methods=['POST'])
@admin_required
def edit_json(id):
    answerForm = ExerciseAnswerForm()
    editing = get_exercise_by_id(id)

    if not editing:
        abort(404)

    if answerForm.validate_on_submit():
        json_data = ast.literal_eval(answerForm.json.data)
        log(current_user, 'exercise', editing.id, 'json.update', old_data=json.dumps(get_exercise_answers(editing)), new_data=json.dumps(json_data))
        create_exercise_files(editing, get_exercise_html(editing), json_data)
        return redirect(url_for('admin.edit_exercise', exercise_id=editing.id))
    return redirect(url_for('admin.admin'))

@bp.route('/exercise/<id>/html', methods=['POST'])
@admin_required
def edit_html(id):
    htmlForm = ExerciseHTMLForm()
    editing = get_exercise_by_id(id)

    if not editing:
        abort(404)

    if htmlForm.validate_on_submit():
        html_data = htmlForm.html.data
        log(current_user, 'exercise', editing.id, 'html.update', old_data=get_exercise_html(editing), new_data=html_data)
        create_exercise_files(editing, html_data, get_exercise_answers(editing))
        return redirect(url_for('admin.edit_exercise', exercise_id=editing.id))
    return redirect(url_for('admin.admin'))

@bp.route('/exercise/<id>/delete', methods=['POST'])
@admin_required
def delete_exercise(id):
    deleteForm = DeleteExerciseForm()
    editing = get_exercise_by_id(id)

    if not editing:
        abort(404)

    if deleteForm.validate_on_submit():
        delete_exercise_files(editing)
        db.session.delete(editing)
        try:
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            db.session.rollback()
        log(current_user, 'exercise', editing.id, 'delete')
        return redirect(url_for('admin.admin'))
    return redirect(url_for('admin.admin'))

# --- Emblem related routes within /admin ---

@bp.route('/emblem/<emblem_id>')
@admin_required
def edit_emblem(emblem_id):
    appearanceForm = EmblemAppearanceForm()
    deleteForm = DeleteEmblemForm()
    editing = get_emblem_by_id(emblem_id)

    if not editing:
        abort(404)

    if request.method == 'GET':
        appearanceForm.name.data = editing.name
        appearanceForm.color.data = editing.color
    
    return render_template('admin/emblem.html', user=current_user, editing=editing,
                           appearanceForm=appearanceForm,
                           deleteForm=deleteForm)

@bp.route('/emblem', methods=['GET','POST'])
@admin_required
def create_emblem():
    createForm = EmblemCreationForm()
    
    if createForm.validate_on_submit():
        emblem = createEmblem(name=createForm.name.data, color=createForm.color.data)
        return redirect(url_for('admin.edit_emblem', emblem_id=emblem.id))
    return render_template('admin/create_emblem.html', user=current_user, createForm=createForm)

@bp.route('/emblem/<emblem_id>/appearance', methods=['POST'])
@admin_required
def edit_emblem_appearance(emblem_id):
    appearanceForm = EmblemAppearanceForm()
    editing = get_emblem_by_id(emblem_id)

    if not editing:
        abort(404)

    if appearanceForm.validate_on_submit():
        editing.name = appearanceForm.name.data
        editing.color = appearanceForm.color.data
        try:
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            db.session.rollback()
        return redirect(url_for('admin.edit_emblem', emblem_id=editing.id))
    return redirect(url_for('admin.admin'))

@bp.route('/emblem/<emblem_id>/delete', methods=['POST'])
@admin_required
def delete_emblem(emblem_id):
    deleteForm = DeleteEmblemForm()
    editing = get_emblem_by_id(emblem_id)

    if not editing:
        abort(404)

    if deleteForm.validate_on_submit():
        db.session.delete(editing)
        try:
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            db.session.rollback()
        return redirect(url_for('admin.admin'))
    return redirect(url_for('admin.admin'))

@bp.route('/tokens/<token_id>/invalidate', methods=['POST'])
@admin_required
def invalidate_tokens(token_id):
    """Path for invalidating tokens."""
    token = get_token_by_id(token_id)
    invalidate_token(token)
    log(current_user, 'token', token.id, 'invalidate')
    return redirect(url_for('admin.tokens'))
