from app.extensions import db
from app.models.logs import Log
from datetime import datetime, timezone

def get_log_by_id(log_id):
    """Retrieve a log entry by its ID."""
    log = Log.query.filter(Log.id == log_id).first()
    if not log:
        return None
    return log

def log(user, entity, affected_id, action, new_data=None, old_data=None):
    """Create a new log entry."""
    if new_data == old_data and new_data:
        return None
    log = Log(
        user_id=user.id if user else 0,
        entity=entity,
        affected_id=affected_id,
        timestamp=int(datetime.now(timezone.utc).timestamp()),
        action=action,
        new_data=new_data,
        old_data=old_data  # Old data can be empty even if data changed has a value
    )
    db.session.add(log)
    db.session.commit()
    return log
