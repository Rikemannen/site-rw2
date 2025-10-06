import time
from app.models.chat import ChatMessage
from app.extensions import db
from sqlalchemy import delete
import sqlalchemy.exc

def get_chat_by_id(msg_id):
    """Retrieve the message object based on its ID."""
    return ChatMessage.query.filter_by(id=msg_id).first()

def get_all_chats(c=75):
    """Retrieve all message objects up to a limit."""
    return ChatMessage.query.limit(c).all()

def delete_chat_message(msg):
    """Delete a chat message."""
    db.session.delete(msg)
    try:
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        db.session.rollback()

def create_chat_message(user_id, content):
    """Create a chat message entry in the database."""
    msg = ChatMessage(
        user_id=user_id,
        content=content,
        timestamp=time.time()
    )
    db.session.add(msg)
    try:
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        db.session.rollback()

def clear_chat():
    """Delete all message columns."""
    db.session.execute(delete(ChatMessage))
    try:
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        db.session.rollback()

def clear_user_messages(user):
    """Delete all messages from a user."""
    for message in user.chat_messages:
        db.session.delete(message)
    try:
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        db.session.rollback()

def purge_chat():
    """Purge chat messages older than 7 days."""
    threshold = time.time() - (7 * 24 * 60 * 60)  # 7 days ago
    old_messages = ChatMessage.query.filter(ChatMessage.timestamp < threshold).all()
    for msg in old_messages:
        db.session.delete(msg)
    try:
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        db.session.rollback()
