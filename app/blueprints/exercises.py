"""Handles exercise-related routes and views."""

import re
import json
import sqlalchemy.exc
from flask_login import login_required
from flask import Blueprint, flash, render_template, url_for, redirect, request, jsonify, abort
from flask_login import current_user as user
from app.services.exercise_service import get_exercise_by_id, liked, unliked, increment_finishes, increment_attempts, create_exercise, delete_exercise
from app.services.file_service import create_exercise_files, get_exercise_html, get_exercise_answers
from app.forms.exercise_forms import CreateExerciseForm, EditExerciseForm, DeleteExerciseForm
from app.extensions import db

bp = Blueprint('exercise', __name__, url_prefix='/exercise')

@bp.route('/<exercise_id>')
def view(exercise_id):
    """Render the exercise page."""
    exercise = get_exercise_by_id(exercise_id)
    if not exercise:
        abort(404)
    if not exercise or not exercise.approved:
        if exercise and user.admin and not exercise.approved:
            return redirect(url_for('admin.preview_exercise', exercise_id=exercise_id))
        abort(404)
    return render_template('exercises/exercise.html', exercise=exercise, show_edit_links=True)

@bp.route('/<exercise_id>/settings', methods=['GET', 'POST'])
@login_required
def settings(exercise_id):
    """Render the exercise settings page."""
    editing = get_exercise_by_id(exercise_id)
    editForm = EditExerciseForm()
    deleteForm = DeleteExerciseForm()
    if not editing:
        abort(404) 
    if not user.owns_exercise(editing):
        abort(403)

    if request.method == 'GET':
        editForm.name.data = editing.name
        editForm.description.data = editing.description
        editForm.public_answers.data = editing.public_answers
        editForm.requires_all.data = editing.requires_all

    if editForm.validate_on_submit():
        editing.name = editForm.name.data
        desc = editForm.description.data.replace("\r\n", "\n").strip()
        # Replace multiple newlines with a single newline
        desc = re.sub(r'\n{2,}', '\n\n', desc)
        # Replace multiple spaces with a single space
        desc = re.sub(r' {2,}', ' ', desc)
        editing.description = desc
        editing.public_answers = editForm.public_answers.data
        editing.requires_all = editForm.requires_all.data
        if editForm.answers.data:
            json_file = editForm.answers.data
            json_content = json_file.read().decode('utf-8')
            data = json.loads(json_content)
            create_exercise_files(editing, get_exercise_html(editing), data)
        if editForm.html.data:
            html_file = editForm.html.data
            html_content = html_file.read().decode('utf-8')
            create_exercise_files(editing, html_content, get_exercise_answers(editing))
    
        try:
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            db.session.rollback()
        flash('Övningen har uppdaterats!', 'success')
        return redirect(url_for('exercise.settings', exercise_id=editing.id))
    
    return render_template('exercises/settings.html', editing=editing, editForm=editForm, deleteForm=deleteForm)

@bp.route('/<exercise_id>/delete', methods=['POST'])
@login_required
def exercise_deletion(exercise_id):
    form = DeleteExerciseForm()
    editing = get_exercise_by_id(exercise_id)

    if not user.owns_exercise(editing):
        abort(403)

    if form.validate_on_submit():
        delete_exercise(editing)

        flash('Övningen har raderats!', 'success')
        return redirect(url_for('exercise.settings', exercise_id=editing.id))
    return redirect(url_for('main.index'))

@bp.route('/<exercise_id>/likes')
def likes(exercise_id):
    """Shows who has liked the exercise."""
    exercise = get_exercise_by_id(exercise_id)
    if not exercise or not exercise.approved:
        return abort(404)

    return render_template('exercises/likes.html', exercise=exercise)

@bp.route('/<exercise_id>/like', methods=['POST'])
@login_required
def like(exercise_id):
    """Makes a user like an exercise. Unlikes if already liked."""
    exercise = get_exercise_by_id(exercise_id)
    if not exercise or not exercise.approved:
        abort(404)

    if user.has_liked_exercise(exercise):
        unliked(user, exercise)
    else:
        liked(user, exercise)

    return redirect(url_for('exercise.view', exercise_id=exercise.id))

@bp.route('/<exercise_id>/submit', methods=['POST'])
def submit(exercise_id):
    """Correct the submitted answers against the exercise answers."""
    exercise = get_exercise_by_id(exercise_id)

    correct_answers = get_exercise_answers(exercise)
    submitted_answers = request.get_json()

    if len(correct_answers) != len(submitted_answers) and exercise.requires_all:
        abort(400)

    results = {}

    for key, val in correct_answers.items():
        submitted = submitted_answers.get(key)

        # split strings and optional boolean
        strings = [v.strip() for v in val if isinstance(v, str)]
        case_sensitive = next((v for v in val if isinstance(v, bool)), False)

        if submitted is None:
            results[key] = False
        else:
            if case_sensitive:
                results[key] = submitted in strings
            else:
                results[key] = submitted.lower() in [s.lower() for s in strings]

        all_correct = all(results.values())

    increment_attempts(exercise)
    if all_correct:
        increment_finishes(exercise)

    return jsonify(results)

@bp.route('/<exercise_id>/answers')
@login_required
def show_answers(exercise_id):
    exercise = get_exercise_by_id(exercise_id)
    if not exercise.public_answers:
        abort(403)
    answers = get_exercise_answers(exercise)

    return jsonify(answers)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new exercise."""
    form = CreateExerciseForm()
    if form.validate_on_submit():
        desc = form.description.data.replace("\r\n", "\n").strip()
        desc = re.sub(r'\n{2,}', '\n\n', desc)
        desc = re.sub(r' {2,}', ' ', desc)
        questions = []
        for key in request.form:
            if key.startswith(("q")):
                questions.append(request.form[key])

        answers = {}
        for key in request.form:
            if key.startswith(("a")):
                answers["q"+key[1:]] = request.form[key]

        html_header = """
<div class="bg-white rounded-2xl shadow-xl p-6">
    <form id="exercise-form" class="space-y-2">"""
        
        html_footer = """
        <button type="button" id="submit-btn" class="button-blue mt-2">Rätta</button>
        <button type="button" id="reveal-btn" class="button-red mt-2">Kolla svar</button>
    </form>
</div>
<script src="/static/exercise_submit.js"></script> <!-- Scriptet som hanterar svaren, ändra inte denna rad -->
"""

        rows_html = ""
        for idx, question in enumerate(questions, 1):
            rows_html += f"""
        <div class="flex items-center">
            <label for="q{idx}" class="w-32">{question}</label>
            <input type="text" id="q{idx}" name="q{idx}" class="border p-1 m-2 flex-1">
        </div>
"""

        full_html = html_header + rows_html + html_footer
        print("full_html", full_html, "\nrows_html", rows_html, "\nquestions/answers", questions, answers)

        exercise = create_exercise(
            name=form.name.data,
            description=desc,
            json_data=answers,
            html_data=full_html,
            owner=user,
            approved=user.verified or user.admin
        )
        if not user.verified and not user.admin:
            flash('Övningen har skapats och kommer att visas när den har godkänts.', 'success')
        return redirect(url_for('exercise.view', exercise_id=exercise.id)) if user.verified or user.admin else redirect(url_for('exercise.create'))
    return render_template('exercises/create.html', form=form)

@bp.route('/create/legacy', methods=['GET', 'POST'])
@login_required
def legacy_create():
    """Create a new exercise."""
    form = CreateExerciseForm()
    if form.validate_on_submit():
        json_file = form.answers.data
        json_content = json_file.read().decode('utf-8')
        html_file = form.html.data
        html_content = html_file.read().decode('utf-8')
        data = json.loads(json_content)
        desc = form.description.data.replace("\r\n", "\n").strip()
        desc = re.sub(r'\n{2,}', '\n\n', desc)
        desc = re.sub(r' {2,}', ' ', desc)
        exercise = create_exercise(
            name=form.name.data,
            description=desc,
            json_data=data,
            html_data=html_content,
            owner=user,
            approved=user.verified or user.admin
        )
        if not user.verified and not user.admin:
            flash('Övningen har skapats och kommer att visas när den har godkänts.', 'success')
        return redirect(url_for('exercise.view', exercise_id=exercise.id)) if user.verified or user.admin else redirect(url_for('exercise.create'))
    return render_template('exercises/create_old.html', form=form)
