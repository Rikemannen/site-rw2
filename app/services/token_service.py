import secrets
import time
from flask import json
import sqlalchemy.exc
from app.models.token import Token
from app.extensions import db

def get_token_by_id(id):
    """Returns the token object based on id."""
    return db.session.query(Token).filter_by(id=id).first()

def get_user_token(user):
    """Get valid token associated with user. (If any.)"""
    token = db.session.query(Token).filter_by(user_id=user.id).filter_by(valid=True).first()
    if not token:
        print("none")
        return None
    print(token, "valid:", token.is_valid)
    return token if token.is_valid else None

def get_token_by_secret(secret):
    """Gets the token object based on token secret."""
    return db.session.query(Token).filter_by(secret=secret).first()

def invalidate_token(token):
    """Invalidate a token."""
    token.valid = False
    db.session.commit()
    return token

def generate_token(user):
    """Create a token for a user."""
    generated = secrets.token_urlsafe(32)
    expires = int(time.time()) + 7 * 24 * 3600 # A week
    token = Token(user_id=user.id, secret=generated, expires=expires)
    user_token = get_user_token(user)
    print("user token to invalidate", user_token)
    if user_token:
        print("yes")
        invalidate_token(user_token)
    print("no if no yes")
    db.session.add(token)
    try:
        db.session.commit()
        return token
    except sqlalchemy.exc.IntegrityError:
        db.session.rollback()
        return None

def get_url(token, host):
    """Get a url to recover account associated with token."""
    return host + "/recover/" + token.secret
