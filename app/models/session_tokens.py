import time
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.extensions import db

class SessionToken(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, db.ForeignKey('users.id'), nullable=False)
    token = Column(String(64), unique=True, nullable=False)
    created = Column(Integer, default=lambda: int(time.time()))
    expires = Column(Integer, nullable=False)
    valid = Column(Boolean, default=True)

    user = relationship('User', back_populates='sessions', foreign_keys=[user_id])
