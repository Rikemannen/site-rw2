from flask import Blueprint, render_template
from flask_socketio import emit
from flask_login import current_user
import bleach
from app.extensions import socketio

bp = Blueprint('chat', __name__, url_prefix='/')

messages = []

@socketio.on('send_message')
def handle_send_message(data):
    """Handle incoming chat messages."""
    if not current_user.is_authenticated:
        return
    message = data.get('message')
    clean_message = bleach.clean(message)
    emit('receive_message',
        {'message': clean_message, 'display_name': current_user.display_name,
         'username': current_user.name, 'id': current_user.id},
         broadcast=True)

    messages.append({"message": clean_message, "display_name": current_user.display_name, "name": current_user.name, "id": current_user.id})

@bp.route('/chat', methods=['GET'])
def chat():
    """Render the chat page."""
    return render_template('chat/chat.html', show_chat_window=False)

@bp.route('/chat/messages', methods=['GET'])
def get_messages():
    """Returns a list with all stored messages along with author data."""
    return messages
