import secrets
import time
import sqlalchemy.exc
from app.models.token import Token
from app.extensions import db

def get_token_by_id(token_id):
    """Returns the token object based on id."""
    return Token.query.filter_by(id=token_id).first()

def get_user_token(user):
    """Get valid token associated with user. (If any.)"""
    token = Token.query.filter_by(user_id=user.id).filter_by(valid=True).first()
    if not token:
        return None
    return token if token.is_valid else None

def get_token_by_secret(secret):
    """Gets the token object based on token secret."""
    return db.session.query(Token).filter_by(secret=secret).first()

def invalidate_token(token):
    """Invalidate a token."""
    if token.is_valid:
        token.valid = False
        token.used_timestamp = time.time()
        db.session.commit()
        from app.services.logging_service import log
        log(None, 'token', token.id, 'invalidated')
    return token

def generate_token(user, creator):
    """Create a token for a user."""
    generated = secrets.token_urlsafe(32)
    token = Token(user_id=user.id, creator_id=creator.id, secret=generated)
    user_token = get_user_token(user)
    if user_token:
        invalidate_token(user_token)
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
