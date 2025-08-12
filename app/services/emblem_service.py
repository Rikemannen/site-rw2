import sqlalchemy.exc
from app.models.emblems import Emblem
from app.extensions import db

def get_emblem_by_id(emblem_id):
    """Fetch an emblem by its ID."""
    return Emblem.query.get(emblem_id)

def create_emblem(name, color):
    """Create a new emblem."""
    emblem = Emblem(name=name, color=color)
    db.session.add(emblem)
    try:
        db.session.commit()
        return emblem
    except sqlalchemy.exc.IntegrityError:
        db.session.rollback()
        return None
