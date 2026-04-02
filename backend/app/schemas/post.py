# 게시물 관련 요청/응답 형식 정의
from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel


class PostCreate(BaseModel):
    source_id: int
    title: str
    author: Optional[str] = None
    content: Optional[str] = None
    published_at: Optional[datetime] = None
    content_hash: str
    category: str = "other"
    tags: Optional[List[str]] = None
    victim_info: Optional[Dict[str, Any]] = None
    original_url: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None


class PostResponse(BaseModel):
    id: int
    source_id: int
    title: str
    author: Optional[str]
    content: Optional[str]
    published_at: Optional[datetime]
    category: str
    tags: Optional[List[str]]
    victim_info: Optional[Dict[str, Any]]
    original_url: Optional[str]
    group: Optional[str] = None
    country: Optional[str] = None
    domain: Optional[str] = None
    screenshot: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PostListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[PostResponse]
