"""Log model for the application. Everything an admin does isn't logged, only the most critical actions."""

from sqlalchemy import Column, Integer, String, Text
from app.extensions import db
from app.services.user_service import get_user_by_id
from app.services.token_service import get_token_by_id
from app.services.exercise_service import get_exercise_by_id

class Log(db.Model):
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref='logs')
    entity = Column(String(100), nullable=False)
    affected_id = Column(Integer, nullable=False)
    timestamp = Column(Integer, nullable=False)
    action = Column(String(50), nullable=False)
    new_data = Column(Text, nullable=True)
    old_data = Column(Text, nullable=True)  # Old data can be empty even if new data has a value

    @property
    def affected_object(self):
        """Return the affected object based on the entity and affected_id."""
        if self.entity == 'user':
            return get_user_by_id(self.affected_id)
        elif self.entity == 'token':
            return get_token_by_id(self.affected_id)
        elif self.entity == 'exercise':
            return get_exercise_by_id(self.affected_id)
        return None

    def __repr__(self):
        return f"<Log(user_id='{self.user_id}', entity='{self.entity}', affected_id='{self.affected_id}', timestamp='{self.timestamp}')>"
