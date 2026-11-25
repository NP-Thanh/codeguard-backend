from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import (
    hash_password,
    validate_password_strength,
    verify_password,
)
from app.models.user import User
from app.schemas.user import ChangePasswordRequest, UserRegister


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


def authenticate_user(
    db: Session,
    identifier: str,
    password: str
) -> User | None:
    user = db.scalar(
        select(User).where(
            or_(
                User.email == identifier,
                User.username == identifier
            )
        )
    )

    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    if not user.is_active:
        return None

    return user


def change_user_password(
    db: Session,
    user: User,
    data: ChangePasswordRequest
) -> None:
    """
    Đổi mật khẩu cho user.
    Raise ValueError với thông báo lỗi cụ thể nếu không hợp lệ.
    """
    # 1. Xác thực mật khẩu hiện tại
    if not verify_password(data.current_password, user.password_hash):
        raise ValueError("Current password is incorrect")

    # 2. Mật khẩu mới không được giống mật khẩu cũ
    if verify_password(data.new_password, user.password_hash):
        raise ValueError("New password must be different from the current password")

    # 3. Kiểm tra confirm trùng khớp
    if data.new_password != data.confirm_password:
        raise ValueError("New password and confirmation do not match")

    # 4. Kiểm tra độ mạnh mật khẩu mới
    errors = validate_password_strength(data.new_password)
    if errors:
        raise ValueError(errors[0])

    # 5. Update DB
    user.password_hash = hash_password(data.new_password)
    db.commit()
