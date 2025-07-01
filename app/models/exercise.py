"""Exercise model for the application."""

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship
from app.extensions import db
from app.models.user import User

class Exercise(db.Model):
    __tablename__ = 'exercises'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(), nullable=False)
    owner_id = Column(Integer, db.ForeignKey('users.id'), nullable=False)
    owner = relationship('User', backref='exercises')
    created = Column(Integer, nullable=False)
    attempts = Column(Integer, default=0)
    finishes = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    approved = Column(Boolean, default=False)

    def __repr__(self):
        return f"<Exercise(name='{self.name}', description='{self.description[:20]}...')>"