"""Application factory for the Flask application."""

from datetime import datetime
from os import environ
from flask import Flask, render_template
from app.blueprints import main, auth, exercises, chat, admin
from app.extensions import login_manager
from app.services.user_service import get_user_by_id
from app.extensions import socketio, db
from flask_login import current_user
from app.blueprints.chat import messages

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    socketio.init_app(app)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
    def datetimeformat(value):
        return datetime.fromtimestamp(value).strftime('%d/%m %H:%M:%S')

    @app.errorhandler(404)
    def not_found(error):
        """Render the 404 Not Found page."""
        return render_template('404.html'), 404
    
    @app.context_processor
    def inject_user():
        return {'user': current_user}
    
    @app.context_processor
    def inject_messages():
        return dict(messages=messages)

    return app
