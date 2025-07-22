"""Token model for the application."""

import time
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from app.extensions import db

class Token(db.Model):
    __tablename__ = 'tokens'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    secret = Column(String(64), nullable=False, unique=True)
    expires = Column(Integer, nullable=False)
    valid = Column(Boolean, nullable=False, default=True)

    @property
    def is_valid(self):
        """Returns boolean telling if the token is valid or not."""
        return int(time.time()) < self.expires and self.valid

    def __repr__(self):
        return f"<Token(id={self.id}, user_id='{self.user_id}', expires='{self.expires}', valid='{self.is_valid}', token='{self.secret[:10]}')>"
