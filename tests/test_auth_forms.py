import pytest
from flask import Flask
from app.forms.auth_forms import LoginForm, SignupForm

@pytest.fixture(scope="module")
def app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test'
    app.config['WTF_CSRF_ENABLED'] = False
    return app

# LoginForm tests
def test_login_form_validates(app):
    with app.app_context():
        form = LoginForm(data={"username": "testuser", "password": "longenoughpassword"})
        assert form.validate()

def test_login_form_invalid_short_username(app):
    with app.app_context():
        form = LoginForm(data={"username": "ab", "password": "longenoughpassword"})
        assert not form.validate()

def test_login_form_invalid_short_password(app):
    with app.app_context():
        form = LoginForm(data={"username": "testuser", "password": "short"})
        assert not form.validate()

# SignupForm tests
def test_signup_form_validates(app):
    with app.app_context():
        form = SignupForm(data={"username": "newuser", "password": "longenoughpassword"})
        assert form.validate()

def test_signup_form_invalid_short_username(app):
    with app.app_context():
        form = SignupForm(data={"username": "ab", "password": "longenoughpassword"})
        assert not form.validate()

def test_signup_form_invalid_short_password(app):
    with app.app_context():
        form = SignupForm(data={"username": "newuser", "password": "short"})
        assert not form.validate()