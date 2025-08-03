"""User model for the application."""

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
    emblems = relationship('Emblem', secondary='user_emblems', backref='owners')
    equipped_emblem_id = Column(Integer, ForeignKey('emblems.id'), nullable=True)
    equipped_emblem = relationship('Emblem', foreign_keys=[equipped_emblem_id])
    admin = Column(Boolean, default=False)
    verified = Column(Boolean, default=False)
    liked_exercises = relationship('Exercise', secondary='exercise_likes', back_populates='liked_by')
    exercises = relationship('Exercise', back_populates='owner')
    name_last_change = Column(Integer, nullable=True)
    joined = Column(Integer, nullable=False, default=0)  # Unix timestamp
    tokens = relationship('Token', back_populates='owner', foreign_keys='Token.user_id')
    created_tokens = relationship('Token', back_populates='creator', foreign_keys='Token.creator_id')

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
    def owned_exercises(self):
        """Return a list of exercises owned by the user."""
        return self.exercises

    @property
    def color(self):
        """Returns the color of the user's equipped emblem"""
        if self.equipped_emblem and self.equipped_emblem.color:
            return self.equipped_emblem.color
        return None
