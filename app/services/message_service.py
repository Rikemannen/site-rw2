import sqlalchemy.exc
import time
from app.models.messages import Message
from app.extensions import db
from app.services.user_service import get_all_users

def get_message_by_id(id):
    """Get a message object based on the id."""
    return Message.query.filter_by(id=id).first()

def send_message(sender, recipient, content):
    """Create a message entry in the database."""
    message = Message(
        sender_id=sender.id,
        recipient_id=recipient.id,
        content=content
    )
    db.session.add(message)
    try:
        db.session.commit()
        return message
    except sqlalchemy.exc.IntegrityError:
        db.session.rollback()
        return None

def get_user_messages(user, c=25):
    """Get a user's received messages, can also include a limit."""
    return Message.query.filter_by(recipient_id=user.id).order_by(Message.timestamp.desc()).limit(c).all()

def get_user_sent_messages(user, c=25):
    """Get a user's sent messages, can also include a limit."""
    return Message.query.filter_by(sender_id=user.id).limit(c).all()

def send_message_to_all(sender, content):
    """Create a message entry for every user in the database."""
    messages = [
        Message(sender_id=sender.id, recipient_id=user.id, content=content, timestamp=time.time())
        for user in get_all_users()
    ]
    db.session.bulk_save_objects(messages)
    try:
        db.session.commit()
        return messages
    except sqlalchemy.exc.IntegrityError:
        db.session.rollback()
        return None

def read_message(message):
    """Mark the message as read."""
    message.read = True
    try:
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        db.session.rollback()

def read_all_messages(user):
    """Set all user's messages as read."""
    Message.query.filter_by(recipient_id=user.id, read=False).update(
        {Message.read: True}, synchronize_session=False
    )
    try:
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        db.session.rollback()

def delete_all_sent_messages(user):
    """Delete all messages sent from user."""
    for message in user.sent_messages:
        db.session.delete(message)
    try:
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        db.session.rollback()

def purge_messages():
    """Delete all messages older than 30 days."""
    threshold = time.time() - (30 * 24 * 60 * 60)
    Message.query.filter(Message.timestamp < threshold).delete(synchronize_session=False)
    try:
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        db.session.rollback()
