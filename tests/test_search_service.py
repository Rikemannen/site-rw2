import types
import pytest
from app.services import search_service

class DummyUser:
    """A dummy user class for testing."""
    def __init__(self, id_, username):
        self.id = id_
        self.username = username

class DummyExercise:
    """A dummy exercise class for testing."""
    def __init__(self, id_, name):
        self.id = id_
        self.name = name

class DummyQuery:
    """A dummy query class to simulate SQLAlchemy query."""
    def __init__(self, items, attr):
        self.items = items
        self.attr = attr

    def filter(self, condition):
        # Only supports ilike and like for username/id/name
        if "ilike" in str(condition):
            value = condition.right.value.replace('%', '')
            filtered = [item for item in self.items if value.lower() in getattr(item, self.attr).lower()]
        elif "like" in str(condition):
            value = condition.right.value.replace('%', '')
            filtered = [item for item in self.items if getattr(item, self.attr).startswith(value)]
        else:
            filtered = []
        return DummyQuery(filtered, self.attr)

    def all(self):
        return self.items

class DummySession:
    """A dummy session to simulate db.session."""
    def __init__(self, users, exercises):
        self.users = users
        self.exercises = exercises

    def query(self, model):
        if model.__name__ == "User":
            return DummyQuery(self.users, "username")
        elif model.__name__ == "Exercise":
            return DummyQuery(self.exercises, "name")
        else:
            return DummyQuery([], "")

@pytest.fixture
def monkey_db(monkeypatch):
    """Fixture to patch db.session in search_service."""
    users = [DummyUser(1, "alice"), DummyUser(2, "bob"), DummyUser(3, "alicia")]
    exercises = [DummyExercise(1, "english"), DummyExercise(2, "german")]
    dummy_db = types.SimpleNamespace(session=DummySession(users, exercises))
    monkeypatch.setattr(search_service, "db", dummy_db)
    monkeypatch.setattr(search_service, "User", DummyUser)
    monkeypatch.setattr(search_service, "Exercise", DummyExercise)
    return users, exercises

def test_search_users(monkey_db):
    """Test searching users by username."""
    users, _ = monkey_db
    results = search_service.search_users("ali")
    assert len(results) == 2
    assert any(u.username == "alice" for u in results)
    assert any(u.username == "alicia" for u in results)

def test_search_users_by_id_partial(monkey_db):
    """Test searching users by partial id."""
    users, _ = monkey_db
    results = search_service.search_users_by_id_partial(1)
    assert len(results) == 1
    assert results[0].username == "alice"

def test_search_exercises(monkey_db):
    """Test searching exercises by name."""
    _, exercises = monkey_db
    results = search_service.search_exercises("ger")
    assert len(results) == 1
    assert results[0].name == "german"

def test_search_exercises_by_id_partial(monkey_db):
    """Test searching exercises by partial id."""
    _, exercises = monkey_db
    results = search_service.search_exercises_by_id_partial(2)
    assert len(results) == 1
    assert results[0].name == "german"
