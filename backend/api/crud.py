from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.common.role import UserRole
from backend.db.models import User


def get_user(db: Session, username: str) -> User | None:
    return db.scalar(
        select(User).where(
            User.username == username,
            User.is_deleted.is_(False),
        )
    )


def create_user(
    db: Session,
    *,
    username: str,
    email: str,
    password_hash: str,
    role: UserRole = UserRole.USER,
) -> User:
    user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
