#수집된 게시물 테이블 - 크롤러가 가져온 데이터가 여기 쌓임
from datetime import datetime
from typing import Optional, List, Any

from sqlalchemy import String, Text, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    author: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, index=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    category: Mapped[str] = mapped_column(String(20), nullable=False, default="other")
    tags: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    victim_info: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    original_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    raw_data: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)

    source: Mapped["Source"] = relationship(back_populates="posts")
    alerts: Mapped[List["Alert"]] = relationship(back_populates="post")
