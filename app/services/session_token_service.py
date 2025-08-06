import secrets
import time
from flask import make_response, redirect, request
from app.models.session_tokens import SessionToken
from app.extensions import db

def create_session_token(user):
    """Create a session token for the user."""
    token = secrets.token_hex(32)
    session_token = SessionToken(
        user_id=user.id,
        token=token,
        expires=int(time.time()) + 60 * 60 * 24 * 7  # 7 days
    )
    db.session.add(session_token)
    db.session.commit()
    return token

def get_user_from_token(token_str):
    """Get the user object associated with a token."""
    token = SessionToken.query.filter_by(token=token_str, valid=True).first()
    if token and token.expires > int(time.time()):
        return token.user
    return None

def invalidate_session_token(token_str):
    """Invalidate specified session token."""
    token = SessionToken.query.filter_by(token=token_str, valid=True).first()
    token.valid = False
    db.session.commit()

def invalidate_all_sessions(user):
    """Invalidate all sessions for a user."""
    for session in user.sessions:
        session.valid = False
    db.session.commit()

def login_user(user):
    """Create session for user and set cookie."""
    token = create_session_token(user)
    resp = make_response(redirect('/'))
    resp.set_cookie('session_token', token, httponly=True, secure=True, samesite='Lax')
    return resp

def logout_user():
    """Invalidate session and delete cookie for user."""
    token = request.cookies.get('session_token')
    if token:
        invalidate_session_token(token)
    resp = make_response(redirect('/login'))
    resp.delete_cookie('session_token')
    return resp
