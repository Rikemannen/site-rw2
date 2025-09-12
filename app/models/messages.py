import time
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.extensions import db

class Message(db.Model):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, db.ForeignKey('users.id'), nullable=False)
    recipient_id = Column(Integer, db.ForeignKey('users.id'), nullable=False)
    content = Column(String(500), nullable=False)
    timestamp = Column(Integer, default=time.time())
    read = Column(Boolean, default=False)

    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    recipient = relationship("User", foreign_keys=[recipient_id], back_populates="received_messages")

    def __repr__(self):
        return f"<Message(sender='{self.sender_id}', recipient='{self.recipient_id}', content='{self.content[:10]}...')>"
