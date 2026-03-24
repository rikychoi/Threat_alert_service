#이메일 유출 조회 요청/응답 형식 정의
from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel


class EmailCheckRequest(BaseModel):
    email: str


class LeakRecord(BaseModel):
    id: int
    source_name: str
    title: str
    category: str
    published_at: Optional[datetime]
    victim_info: Optional[Dict[str, Any]]


class EmailCheckResponse(BaseModel):
    email: str
    is_leaked: bool
    leak_count: int
    records: List[LeakRecord]
