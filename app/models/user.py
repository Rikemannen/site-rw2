"""User model for the application."""

import time
from sqlalchemy import Column, Integer, String, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from app.extensions import db

user_emblems = Table(
    'user_emblems',
    db.Model.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('emblem_id', Integer, ForeignKey('emblems.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(20), unique=True, nullable=False)
    display_name = Column(String(20), nullable=True, default=None)
    password_hash = Column(String(), nullable=False)
    equipped_emblem_id = Column(Integer, ForeignKey('emblems.id'), nullable=True)
    admin = Column(Boolean, default=False)
    verified = Column(Boolean, default=False)
    name_last_change = Column(Integer, nullable=True)
    joined = Column(Integer, nullable=False, default=time.time())
    description = Column(String(1000), nullable=True)
    listed = Column(Boolean, default=True)
    banned_until = Column(Integer, nullable=True)
    last_login = Column(Integer, nullable=True)

    emblems = relationship('Emblem', secondary='user_emblems', backref='owners')
    equipped_emblem = relationship('Emblem', foreign_keys=[equipped_emblem_id])
    exercises = relationship('Exercise', back_populates='owner')
    liked_exercises = relationship('Exercise', secondary='exercise_likes', back_populates='liked_by')
    created_tokens = relationship('Token', back_populates='creator', foreign_keys='Token.creator_id')
    tokens = relationship('Token', back_populates='owner', foreign_keys='Token.user_id')
    sessions = relationship('SessionToken', back_populates='user', foreign_keys='SessionToken.user_id')
    sent_messages = relationship("Message", foreign_keys='Message.sender_id', back_populates="sender")
    received_messages = relationship("Message", foreign_keys='Message.recipient_id', back_populates="recipient")
    chat_messages = relationship("ChatMessage", back_populates='user')

    # Additional columns to consider:
    #profile_picture = Column(String(), nullable=True) # Url
    #profile_banner = Column(String(), nullable=True) # Url

    def __repr__(self):
        return f"<User(username='{self.name}', password_hash='***')>"

    def owns_exercise(self, exercise):
        """Check if the user owns a specific exercise."""
        return exercise.owner_id == self.id

    def has_liked_exercise(self, exercise):
        """Check if user has liked an exercise."""
        return self in exercise.liked_by

    @property
    def banned(self):
        """Returns boolean if user is banned."""
        return self.banned_until and self.banned_until > int(time.time())

    @property
    def color(self):
        """Returns the color of the user's equipped emblem"""
        if self.equipped_emblem and self.equipped_emblem.color:
            return self.equipped_emblem.color
        return None
