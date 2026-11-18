from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine( # tạo engine quản lý kết nối Database
    settings.database_url,
    pool_pre_ping=True # kiểm tra connection trước khi sử dụng
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)