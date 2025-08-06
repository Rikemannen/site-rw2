from flask import Blueprint, render_template
from flask_socketio import emit
from flask_login import current_user
import bleach
import time
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from collections import deque
from app.extensions import socketio
from app.services.user_service import get_user_by_id

bp = Blueprint('chat', __name__, url_prefix='/')

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["120 per hour"]
)

messages = deque(maxlen=75)

@socketio.on('send_message')
@limiter.limit("3 per second")
def handle_send_message(data):
    """Handle incoming chat messages."""
    if not current_user.is_authenticated:
        return
    message = data.get('message')
    if len(message) > 100:
        return
    color = "#949494"
    if current_user.equipped_emblem:
        color = current_user.equipped_emblem.color
    clean_message = bleach.clean(message)
    now = time.time()
    emit('receive_message',
        {'message': clean_message, 'display_name': current_user.display_name,
         'name': current_user.name, 'id': current_user.id, 'color': color, 'time': now},
         broadcast=True)

    messages.append({"message": clean_message, "id": current_user.id, "time": now})

@bp.route('/chat', methods=['GET'])
def chat():
    """Render the chat page."""
    return render_template('chat/chat.html', show_chat_window=False)

@bp.route('/chat/messages', methods=['GET'])
def get_messages():
    """Returns a list with all stored messages along with author data."""
    result = []
    for msg in messages:
        user = get_user_by_id(msg["id"])
        color = "#949494"
        if user and user.equipped_emblem:
            color = user.equipped_emblem.color
        
        if user:
            result.append({
                "message": msg["message"],
                "display_name": user.display_name,
                "name": user.name,
                "id": user.id,
                "color": color,
                "time": msg["time"]
            })

    return result
