from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO

db = SQLAlchemy()
login_manager = LoginManager()

# DO NOT set message_queue here; pass it during init_app
# Damn ok chill
socketio = SocketIO()
