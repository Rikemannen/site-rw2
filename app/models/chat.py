"""Chat message model for the application."""

import time
from app.extensions import db
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

class ChatMessage(db.Model):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, db.ForeignKey("users.id"), nullable=False)
    timestamp = Column(String, default=time.time())
    content = Column(String(100), nullable=False)

    user = relationship("User", foreign_keys=[user_id], back_populates="chat_messages")

    def __repr__(self):
        return f"<ChatMessage(content='{self.content}', timestamp='{self.timestamp}', user_id='{self.user_id}')>"
