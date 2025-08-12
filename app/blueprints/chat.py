from flask import Blueprint, render_template, redirect, url_for
from flask_socketio import emit
from flask_login import current_user
import bleach
import time
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from collections import deque
from app.extensions import socketio
from app.services.chat_message_service import create_chat_message, get_all_chats, clear_chat
from app.utils.security import admin_required

bp = Blueprint('chat', __name__, url_prefix='/')

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["120 per hour"]
)

@socketio.on('send_message')
def handle_send_message(data):
    """Handle incoming chat messages."""
    if not current_user.is_authenticated:
        return
    message = data.get('message')
    if len(message) > 100:
        return
    color = "#949494"
    if current_user.equipped_emblem:
        color = current_user.equipped_emblem.color if not current_user.equipped_emblem.name in {"Rainbow", "Shift", "Regnbåge"} else "shift"
    clean_message = bleach.clean(message)
    now = time.time()
    emit('receive_message',
        {'message': clean_message, 'display_name': current_user.display_name,
         'name': current_user.name, 'id': current_user.id, 'color': color, 'time': now},
         broadcast=True)

    create_chat_message(current_user.id, clean_message)

@bp.route('/chat', methods=['GET'])
def chat():
    """Render the chat page."""
    return render_template('chat/chat.html', show_chat_window=False)

@bp.route('/chat/messages', methods=['GET'])
def get_messages():
    """Returns a list with all stored messages along with author data."""
    result = []
    messages = get_all_chats()
    for msg in messages:
        user = msg.user
        color = "#949494"
        if user and user.equipped_emblem:
            color = user.equipped_emblem.color if not user.equipped_emblem.name in {"Rainbow", "Shift", "Regnbåge"} else "shift"
        
        if user:
            result.append({
                "message": msg.content,
                "display_name": user.display_name,
                "name": user.name,
                "id": user.id,
                "color": color,
                "time": msg.timestamp
            })

    return result

@bp.route('/chat/clear', methods=['POST'])
@admin_required
def clear():
    """Handle clearing the chat."""
    clear_chat()
    return redirect(url_for('admin.admin'))
