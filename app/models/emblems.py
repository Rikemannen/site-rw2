"""Emblem model for the application."""

from sqlalchemy import Column, Integer, String
from app.extensions import db

class Emblem(db.Model):
    __tablename__ = 'emblems'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    color = Column(String(7), nullable=False, default="#FFFFFF")  # Hex color code

    def __repr__(self):
        return f"<Emblem(name='{self.name}', color='{self.color}')>"
