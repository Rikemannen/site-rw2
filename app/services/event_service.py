import time
from app.extensions import db
from app.models.events import Event

def get_event(event_type):
    """Get the event object based on type."""
    event = Event.query.filter(Event.event_type == event_type).first()
    if not event:
        return None
    return event

def create_event(event_type, data, expires=time.time() + 259200): # expiry is today + 3 days by default
    """Create an event."""
    event = Event(
        event_type=event_type,
        data=data,
        expires=expires
    )
    db.session.add(event)
    try:
        db.session.commit()
        return event
    except sqlalchemy.exc.IntegrityError:
        db.session.rollback()
        return None

def get_all_events():
    """Return all events (that have not expired)."""
    return Event.query.filter(
        (Event.expires == None) | (Event.expires > time.time())
    ).all()

def delete_event(event):
    """Delete an event"""
    db.session.delete(event)
    try:
        db.session.commit()
        return event
    except sqlalchemy.exc.IntegrityError:
        db.session.rollback()
        return None
