from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import get_password_hash
from app.models.setting import UserSetting
from app.models.user import User


def bootstrap_admin_user(db: Session) -> None:
    settings = get_settings()
    existing = db.query(User).first()
    if existing:
        return

    user = User(email=settings.admin_email, hashed_password=get_password_hash(settings.admin_password), is_active=True)
    db.add(user)
    db.flush()

    user_settings = UserSetting(user_id=user.id, timezone=settings.default_timezone)
    db.add(user_settings)
    db.commit()
