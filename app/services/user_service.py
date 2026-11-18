from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserRegister


def register_user(db: Session, user_data: UserRegister) -> User:
    existing_user = db.scalar(
        select(User).where(
            or_(
                User.email == str(user_data.email),
                User.username == user_data.username
            )
        )
    )

    if existing_user:
        if existing_user.email == str(user_data.email):
            raise ValueError("Email already registered")

        raise ValueError("Username already taken")

    user = User(
        full_name=user_data.full_name,
        email=str(user_data.email),
        username=user_data.username,
        password_hash=hash_password(user_data.password)
    )

    db.add(user)

    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise ValueError("Email or username already exists")

    return user