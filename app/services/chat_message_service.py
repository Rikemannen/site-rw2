import time
from app.models.chat import ChatMessage
from app.extensions import db
from sqlalchemy import delete

def get_chat_by_id(msg_id):
    """Retrieve the message object based on its ID."""
    return ChatMessage.query.filter_by(id=msg_id).first()

def get_all_chats(c=75):
    """Retrieve all message objects up to a limit."""
    return ChatMessage.query.limit(c).all()

def delete_chat_message(msg):
    """Delete a chat message."""
    db.session.delete(msg)
    db.commit()

def create_chat_message(user_id, content):
    """Create a chat message entry in the database."""
    msg = ChatMessage(
        user_id=user_id,
        content=content,
        timestamp=time.time()
    )
    db.session.add(msg)
    db.session.commit()

def clear_chat():
    """Delete all message columns."""
    db.session.execute(delete(ChatMessage))
    db.session.commit()

def clear_user_messages(user):
    """Delete all messages from a user."""
    for message in user.chat_messages:
        db.session.delete(message)
    db.session.commit()