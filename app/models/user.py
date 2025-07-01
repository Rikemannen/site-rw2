"""User model for the application."""

from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from app.extensions import db
from app.models.emblems import Emblem

user_emblems = Table(
    'user_emblems',
    db.Model.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('emblem_id', Integer, ForeignKey('emblems.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(20), unique=True, nullable=False)
    display_name = Column(String(20), nullable=False)
    password_hash = Column(String(), nullable=False)
    emblems = relationship('Emblem', secondary='user_emblems', backref='owners')
    equipped_emblem_id = Column(Integer, ForeignKey('emblems.id'), nullable=True)
    equipped_emblem = relationship('Emblem', foreign_keys=[equipped_emblem_id])
    # More profile related columns, still included tho

    # Additional columns to consider:
    #profile_picture = Column(String(), nullable=True) # Url
    #profile_banner = Column(String(), nullable=True) # Url

    def __repr__(self):
        return f"<User(username='{self.username}', password_hash='***')>"

    def owns_exercise(self, exercise):
        """Check if the user owns a specific exercise."""
        return exercise.owner_id == self.id
