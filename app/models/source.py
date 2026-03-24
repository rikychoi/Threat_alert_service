#크롤링 대상 사이트 테이블 - 어디서 데이터 긁어오는지 관리
from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, DateTime, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    site_type: Mapped[str] = mapped_column(String(20), nullable=False, default="forum")
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    last_crawled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    posts: Mapped[List["Post"]] = relationship(back_populates="source")
