# 크롤링 대상 사이트 요청/응답 형식 - sources CRUD에서 씀
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SourceCreate(BaseModel):
    name: str
    url: str
    site_type: str = "forum"
    description: Optional[str] = None


class SourceUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    site_type: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class SourceResponse(BaseModel):
    id: int
    name: str
    url: str
    site_type: str
    description: Optional[str]
    last_crawled_at: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
