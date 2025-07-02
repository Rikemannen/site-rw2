"""Exercise model for the application."""

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship
from app.extensions import db
from app.models.user import User

exercise_likes = db.Table(
    'exercise_likes',
    db.Model.metadata,
    Column('user_id', Integer, db.ForeignKey('users.id'), primary_key=True),
    Column('exercise_id', Integer, db.ForeignKey('exercises.id'), primary_key=True)
)

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
    approved = Column(Boolean, default=False)
    liked_by = relationship('User', secondary='exercise_likes', back_populates='liked_exercises')

    def likes(self):
        """Return the number of likes for the exercise."""
        return len(self.liked_by)

    def __repr__(self):
        return f"<Exercise(name='{self.name}', description='{self.description[:20]}...')>"
