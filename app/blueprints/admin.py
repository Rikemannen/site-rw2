from flask import Blueprint, json, render_template, request, abort, redirect, url_for, flash
import ast
from flask_login import current_user as user
from app.models.user import User
from app.models.exercise import Exercise
from app.utils.security import admin_required
from app.services.user_service import get_user_by_id
from app.services.exercise_service import get_exercise_by_id
from app.services.token_service import generate_token, get_url
from app.services.file_service import create_exercise_files, delete_exercise_files, get_exercise_html, get_exercise_answers
from app.services.emblem_service import get_emblem_by_id, create_emblem as createEmblem
from app.services.logging_service import log
from app.models.logs import Log
from app.models.emblems import Emblem
from app.extensions import db
from app.forms.admin_forms import (
    ProfileSettingsForm,
    EmblemAssignmentForm,
    UsernameChangeForm,
    PasswordResetForm,
    DeleteUserForm,
    VerifyUserForm,
    ElevateUserForm,
    ExerciseInfoForm,
    ExerciseDataForm,
    ExerciseStatisticForm,
    ExerciseHTMLForm,
    ExerciseAnswerForm,
    DeleteExerciseForm,
    EmblemAppearanceForm,
    DeleteEmblemForm,
    EmblemCreationForm
)

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/')
@admin_required
def admin():
    """Render the base admin page."""
    user_count = User.query.count()
    exercise_count = Exercise.query.count()
    latest_user = User.query.order_by(User.joined.desc()).first()
    total_attempts = db.session.query(db.func.sum(Exercise.attempts)).scalar() or 0
    total_completions = db.session.query(db.func.sum(Exercise.finished)).scalar() or 0
    return render_template('admin/admin.html', user_count=user_count, exercise_count=exercise_count,
                           latest_user=latest_user, attempt_count=total_attempts,
                           completed_count=total_completions)

@bp.route('/logs')
@admin_required
def logs():
    """Render the logs page."""
    count = request.args.get('c', default=100, type=int)
    logs = db.session.query(Log).order_by(Log.id.desc()).limit(count).all()
    return render_template('admin/logs.html', logs=logs)

# --- User related routes within /admin. ---

@bp.route('/user')
@admin_required
def users():
    """Render the user search page."""
    return redirect(url_for('main.search', q='*', type='users'))

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

    if not editing:
        abort(404)

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

    if not editing:
        abort(404)

    emblemForm.emblems.choices = [(e.id, e.name) for e in Emblem.query.all()]
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

    if not editing:
        abort(404)

    if usernameForm.validate_on_submit():
        log(user, 'user', editing.id, 'name.change', old_data=editing.name, new_data=usernameForm.username.data)
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

    if not editing:
        abort(404)

    if resetForm.validate_on_submit():
        token = generate_token(editing)
        url = get_url(token, request.host)
        log(user, 'user', editing.id, 'recovery.token_generated', new_data=json.dumps({'id': token.id, 'token': token.secret[:10] + '...'}))
        log(user, 'token', token.id, 'created', new_data=json.dumps({'token': token.secret[:10] + '...', 'expires': token.expires}))
        flash(url)
        return redirect(url_for('admin.edit_user', user_id=editing.id))
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
        db.session.delete(editing)
        db.session.commit()
        log(user, 'user', editing.id, 'delete')
        return redirect(url_for('admin.admin'))
    return redirect(url_for('admin.admin'))

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
        db.session.commit()
        log(user, 'user', editing.id, 'verified.verify' if verifyForm.verified.data else 'verified.unverify')
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
        db.session.commit()
        log(user, 'user', editing.id, 'admin.elevate' if elevateForm.admin.data else 'admin.demote')
        return redirect(url_for('admin.edit_user', user_id=editing.id))
    return redirect(url_for('admin.admin'))

# --- Exercise related routes within /admin. ---

@bp.route('/exercise')
@admin_required
def exercises():
    """Render the exercise search page."""
    return redirect(url_for('main.search', q='*', type='exercises'))

@bp.route('/exercise/<id>')
@admin_required
def edit_exercise(id):
    infoForm = ExerciseInfoForm()
    dataForm = ExerciseDataForm()
    statisticForm = ExerciseStatisticForm()
    htmlForm = ExerciseHTMLForm()
    answerForm = ExerciseAnswerForm()
    deleteForm = DeleteExerciseForm()
    editing = get_exercise_by_id(id)

    if not editing:
        abort(404)

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

    return render_template('admin/exercise.html', user=user, editing=editing,
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
        editing.description = infoForm.description.data
        db.session.commit()
        return redirect(url_for('admin.edit_exercise', id=editing.id))
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
            log(user, 'exercise', editing.id, 'approve' if dataForm.approved.data else 'unapprove')
        if dataForm.owner.data != editing.owner_id or dataForm.created.data != editing.created:
            log(user, 'exercise', editing.id, 'static.update', old_data=json.dumps({
                'owner_id': editing.owner_id,
                'created': editing.created
            }), new_data=json.dumps({
                'owner_id': dataForm.owner.data,
                'created': dataForm.created.data
            }))
        editing.owner_id = dataForm.owner.data
        editing.created = dataForm.created.data
        editing.approved = dataForm.approved.data
        db.session.commit()
        return redirect(url_for('admin.edit_exercise', id=editing.id))
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
        db.session.commit()
        return redirect(url_for('admin.edit_exercise', id=editing.id))
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
        log(user, 'exercise', editing.id, 'json.update', old_data=json.dumps(get_exercise_answers(editing)), new_data=json.dumps(json_data))
        create_exercise_files(editing, get_exercise_html(editing), json_data)
        return redirect(url_for('admin.edit_exercise', id=editing.id))
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
        log(user, 'exercise', editing.id, 'html.update', old_data=get_exercise_html(editing), new_data=html_data)
        create_exercise_files(editing, html_data, get_exercise_answers(editing))
        return redirect(url_for('admin.edit_exercise', id=editing.id))
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
        db.session.commit()
        log(user, 'exercise', editing.id, 'delete')
        return redirect(url_for('admin.admin'))
    return redirect(url_for('admin.admin'))

# --- Emblem related routes within /admin ---

@bp.route('/emblem/<id>')
@admin_required
def edit_emblem(id):
    appearanceForm = EmblemAppearanceForm()
    deleteForm = DeleteEmblemForm()
    editing = get_emblem_by_id(id)

    if not editing:
        abort(404)

    if request.method == 'GET':
        appearanceForm.name.data = editing.name
        appearanceForm.color.data = editing.color
    
    return render_template('admin/emblem.html', user=user, editing=editing,
                           appearanceForm=appearanceForm,
                           deleteForm=deleteForm)

@bp.route('/emblem', methods=['GET','POST'])
@admin_required
def create_emblem():
    createForm = EmblemCreationForm()
    
    if createForm.validate_on_submit():
        emblem = createEmblem(name=createForm.name.data, color=createForm.color.data)
        return redirect(url_for('admin.edit_emblem', id=emblem.id))
    return render_template('admin/create_emblem.html', user=user, createForm=createForm)

@bp.route('/emblem/<id>/appearance', methods=['POST'])
@admin_required
def edit_emblem_appearance(id):
    appearanceForm = EmblemAppearanceForm()
    editing = get_emblem_by_id(id)

    if not editing:
        abort(404)

    if appearanceForm.validate_on_submit():
        editing.name = appearanceForm.name.data
        editing.color = appearanceForm.color.data
        db.session.commit()
        return redirect(url_for('admin.edit_emblem', id=editing.id))
    return redirect(url_for('admin.admin'))

@bp.route('/emblem/<id>/delete', methods=['POST'])
@admin_required
def delete_emblem(id):
    deleteForm = DeleteEmblemForm()
    editing = get_emblem_by_id(id)

    if not editing:
        abort(404)

    if deleteForm.validate_on_submit():
        db.session.delete(editing)
        db.session.commit()
        return redirect(url_for('admin.admin'))
    return redirect(url_for('admin.admin'))
