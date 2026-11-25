import re
import uuid
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app.core.config import settings

password_hash = PasswordHash.recommended()

# Yêu cầu mật khẩu mạnh:
# - Tối thiểu 8 ký tự
# - Ít nhất 1 chữ hoa
# - Ít nhất 1 chữ thường
# - Ít nhất 1 chữ số
# - Ít nhất 1 ký tự đặc biệt
_PASSWORD_PATTERN = re.compile(
    r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};\'\":,.<>?/\\|`~]).{8,128}$'
)


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def validate_password_strength(password: str) -> list[str]:
    """
    Kiểm tra độ mạnh của mật khẩu.
    Trả về danh sách lỗi (rỗng = hợp lệ).
    """
    errors: list[str] = []

    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    if len(password) > 128:
        errors.append("Password must not exceed 128 characters")
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one digit")
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\'\":,.<>?/\\|`~]', password):
        errors.append("Password must contain at least one special character")

    return errors


def create_access_token(user_id: int) -> str:
    jti = str(uuid.uuid4())
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload = {
        "sub": str(user_id),
        "exp": expire,
        "jti": jti
    }

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.algorithm
    )


def decode_token(token: str) -> dict:
    """
    Decode và trả về payload. Raise jwt.InvalidTokenError nếu không hợp lệ.
    """
    return jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.algorithm]
    )
