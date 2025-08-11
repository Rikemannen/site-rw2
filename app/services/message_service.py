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
    db.session.commit()
    return message

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
    db.session.commit()
    return messages

def read_message(message):
    """Mark the message as read."""
    message.read = True
    db.session.commit()

def read_all_messages(user):
    """Set all user's messages as read."""
    Message.query.filter_by(recipient_id=user.id, read=False).update(
        {Message.read: True}, synchronize_session=False
    )
    db.session.commit()
