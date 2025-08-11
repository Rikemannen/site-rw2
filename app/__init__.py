"""Application factory for the Flask application."""

from datetime import datetime, timedelta
from os import environ
from flask import Flask, render_template, redirect, url_for, request
from flask_login import current_user
from flask_wtf.csrf import CSRFProtect
import logging
from redis import Redis
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.blueprints.chat import get_messages
from app.blueprints import main, auth, exercises, chat, admin, messaging
from app.extensions import login_manager
from app.services.user_service import get_user_by_id
from app.services.session_token_service import get_user_from_token
from app.extensions import socketio, db

redis_client = Redis(host="localhost", port=6379, db=0)

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["120 per hour"],
    storage_uri="redis://localhost:6379"
)

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    socketio.init_app(app)
    csrf = CSRFProtect(app)
    logging.basicConfig(filename='error.log', level=logging.WARNING)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(weeks=1)
    app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024  # 4MB

    db.init_app(app)
    limiter.init_app(app)

    if 'SECRET_KEY' in environ:
        app.config['SECRET_KEY'] = environ['SECRET_KEY']
    else:
        raise KeyError("SECRET_KEY not found in environment variables")

    # Register the main blueprints
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(exercises.bp)
    app.register_blueprint(chat.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(messaging.bp)

    login_manager.init_app(app)

    @login_manager.request_loader
    def load_user_from_request(request):
        token = request.cookies.get('session_token')
        if not token:
            return None
        return get_user_from_token(token)

    @app.template_filter('datetimeformat')
    def datetimeformat(value, variant="full"):
        try:
            # Accept numeric string or int/float timestamp
            ts = int(value)
        except (ValueError, TypeError):
            return None
        dt = datetime.fromtimestamp(value)
        if variant == "full":
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        elif variant == "datetime":
            return dt.strftime('%d/%m %H:%M')
        elif variant == "time":
            return dt.strftime('%H:%M:%S')
        elif variant == "date":
            return dt.strftime('%Y-%m-%d')
        return dt.strftime('%Y-%m-%d %H:%M:%S') # Fallback

    @app.template_filter('format_user')
    def format_user(user):
        """Format user object for display."""
        if user:
            return f"{user.display_name} (@{user.name})" if user.display_name else user.name
        return None

    @app.template_filter('format_user_id')
    def format_user_id(id):
        """Format user object for display."""
        user = get_user_by_id(id)
        return format_user(user)

    @app.errorhandler(404)
    def not_found(error):
        """Render the 404 Not Found page."""
        return render_template('404.html'), 404

    @app.errorhandler(403)
    def forbidden(error):
        """Render the 403 Not Found page."""
        return render_template('403.html'), 403

    @app.errorhandler(401)
    def unauthorized(error):
        """Redirect to login route if user needs to be logged in."""
        return redirect(url_for('auth.login', next=request.url)), 401

    @app.errorhandler(500)
    def server_error(error):
        """Render the 500 Internal server error page."""
        return render_template('500.html'), 500

    @app.errorhandler(429)
    def rate_limit(e: Exception):
        """Render the 429 Rate limit exceeded page."""
        return render_template('429.html'), 429

    @app.context_processor
    def inject_user():
        return dict(current_user=current_user)

    @app.context_processor
    def inject_messages():
        return dict(messages=get_messages())

    @app.context_processor
    def inject_show_banner():
        show_banner = request.cookies.get('saw_banner') != 'yes'
        return dict(show_banner=show_banner)

    return app
