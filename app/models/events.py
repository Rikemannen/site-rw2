"""Event model for the application."""

import time
from sqlalchemy import Column, Integer, String, JSON
from app.extensions import db

class Event(db.Model):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    created = Column(Integer, nullable=False, default=time.time())
    expires = Column(Integer, nullable=True) # Events can last forever, and can be removed at any time by admins
    event_type = Column(String(50), nullable=False)
    data = Column(JSON, nullable=False)

    def __repr__(self):
        return f"<Event(event_type='{self.event_type}', created='{self.created}', expires='{self.expires}')>"
