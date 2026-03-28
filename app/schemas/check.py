# 유출 조회 요청/응답 형식 - 프론트에서 category(group/country/victim_info) + query로 검색
from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel


class CheckRequest(BaseModel):
    category: str
    query: Optional[str] = None


class LeakRecord(BaseModel):
    id: int
    source_name: str
    title: str
    author: Optional[str]
    category: str
    group: Optional[str]
    country: Optional[str]
    domain: Optional[str]
    published_at: Optional[datetime]
    victim_info: Optional[Dict[str, Any]]
    screenshot: Optional[str]


class CrawlerRecord(BaseModel):
    email: str
    found_on: List[str]


class CheckResponse(BaseModel):
    category: str
    query: Optional[str]
    is_leaked: bool
    leak_count: int
    records: List[LeakRecord]
    crawler_results: Optional[CrawlerRecord]
