"""Handles messaging related routes and views. (also includes notifications)"""

import re
from flask import Blueprint, redirect, url_for, flash, render_template, abort, request
from flask_login import current_user, login_required
from flask_socketio import join_room
from app.extensions import socketio
from app.services.message_service import send_message, read_message, read_all_messages, get_user_messages, get_message_by_id
from app.services.user_service import get_user_by_id, get_all_users
from app.forms.message_forms import SendMessageForm

bp = Blueprint('messaging', __name__)

@socketio.on('join')
def on_join(data):
    user_id = data['user_id']
    join_room(str(user_id))

@bp.route('/messages')
@login_required
def messages():
    """Show a user's messages."""
    form = SendMessageForm()
    messages = get_user_messages(current_user)
    form.recipient.choices = [
        (u.id, u.name if not u.display_name or u.display_name == u.name else f"{u.name} (@{u.display_name})", u.color) for u in get_all_users() if u.id != current_user.id
    ]
    r = request.args.get('r')
    if r and r.isdigit():
        form.recipient.data = int(r)
    form.content.data = request.args.get('c', '')
    return render_template('messages.html', messages=messages, form=form)

@bp.route('/send', methods=['POST'])
@login_required
def send():
    """Send a message to a user."""
    form = SendMessageForm()
    form.recipient.choices = [
        (u.id, u.name, u.color) for u in get_all_users() if u.id != current_user.id
    ]

    if form.validate_on_submit():
        recipient = get_user_by_id(form.recipient.data)
        sender = current_user
        content = form.content.data.replace("\r\n", "\n").strip()
        content = re.sub(r'\n{2,}', '\n\n', content)
        content = re.sub(r' {2,}', ' ', content)

        msg = send_message(recipient=recipient, sender=sender, content=content)
        flash('Meddelandet har skickats!')
        socketio.emit(
            'new_message',
            {'id': msg.id, 'sender': msg.sender.name, 'content': msg.content},
            room=str(msg.recipient.id)
        )
    return redirect(url_for('messaging.messages'))

@bp.route('/<message_id>/read', methods=['POST'])
@login_required
def read(message_id):
    message = get_message_by_id(message_id)

    if not message or not message.recipient == current_user:
        abort(404)

    read_message(message)
    return redirect(url_for('messaging.messages'))

@bp.route('/read-all', methods=['POST'])
@login_required
def read_all():
    read_all_messages(current_user)
    return redirect(url_for('messaging.messages'))
