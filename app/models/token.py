"""Token model for the application."""

import time
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.extensions import db

class Token(db.Model):
    __tablename__ = 'tokens'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    owner = relationship('User', back_populates='tokens', foreign_keys=[user_id])
    creator_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    creator = relationship('User', back_populates='created_tokens', foreign_keys=[creator_id])
    secret = Column(String(64), nullable=False, unique=True)
    created = Column(Integer, nullable=False, default=time.time())
    expires = Column(Integer, nullable=False, default=(time.time() + 7 * 24 * 3600))
    valid = Column(Boolean, nullable=False, default=True)
    used_timestamp = Column(Integer)

    @property
    def is_valid(self):
        """Returns boolean telling if the token is valid or not."""
        return int(time.time()) < self.expires and self.valid

    def __repr__(self):
        return f"<Token(id={self.id}, user_id='{self.user_id}', expires='{self.expires}', valid='{self.is_valid}', token='{self.secret[:10]}')>"
