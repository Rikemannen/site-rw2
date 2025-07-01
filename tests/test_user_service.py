import types
import pytest
from app.services import user_service

class DummyUser:
    def __init__(self, id, username):
        self.id = id
        self.username = username

class DummyQuery:
    def __init__(self, users):
        self.users = users
    def filter_by(self, **kwargs):
        for user in self.users:
            if all(getattr(user, k) == v for k, v in kwargs.items()):
                return types.SimpleNamespace(first=lambda: user)
        return types.SimpleNamespace(first=lambda: None)

class DummySession:
    def __init__(self, users):
        self.users = users
    def query(self, model):
        return DummyQuery(self.users)

@pytest.fixture
def monkey_db(monkeypatch):
    users = [DummyUser(1, "alice"), DummyUser(2, "bob")]
    dummy_db = types.SimpleNamespace(session=DummySession(users))
    monkeypatch.setattr(user_service, "db", dummy_db)
    monkeypatch.setattr(user_service, "User", DummyUser)
    return users

def test_get_user_by_id(monkey_db):
    user = user_service.get_user_by_id(1)
    assert user.username == "alice"
    assert user_service.get_user_by_id(999) is None

def test_get_user_by_username(monkey_db):
    user = user_service.get_user_by_username("bob")
    assert user.id == 2
    assert user_service.get_user_by_username("nobody") is None
