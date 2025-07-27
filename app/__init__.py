"""Application factory for the Flask application."""

from datetime import datetime, timedelta
from os import environ
from flask import Flask, render_template, redirect, url_for, request
from flask_login import current_user
from app.blueprints.chat import get_messages
from app.blueprints import main, auth, exercises, chat, admin
from app.extensions import login_manager
from app.services.user_service import get_user_by_id
from app.extensions import socketio, db

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    socketio.init_app(app)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(weeks=1)

    db.init_app(app)

    if 'SECRET_KEY' in environ:
        app.config['SECRET_KEY'] = environ['SECRET_KEY']
    else:
        raise KeyError("SECRET_KEY not found in environment variables")

    # Register the main blueprint
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(exercises.bp)
    app.register_blueprint(chat.bp)
    app.register_blueprint(admin.bp)

    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        """Load a user by their ID."""
        return get_user_by_id(user_id)

    @app.template_filter('datetimeformat')
    def datetimeformat(value, variant="full"):
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
        return redirect(url_for('auth.login', next=request.url))
    
    @app.context_processor
    def inject_user():
        return {'current_user': current_user}
    
    @app.context_processor
    def inject_messages():
        return dict(messages=get_messages())

    return app
