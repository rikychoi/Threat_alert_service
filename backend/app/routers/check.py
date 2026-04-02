# 유출 조회 - group/country/victim_info 카테고리별 검색
from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_, String

from app.database import get_db
from app.models.post import Post
from app.models.source import Source
from app.models.crawler_models import CrawlerEmail
from app.schemas.check import (
    CheckRequest, CheckResponse, LeakRecord, CrawlerRecord
)

router = APIRouter()


def extract_from_raw(raw_data, key):
    if raw_data and isinstance(raw_data, dict):
        return raw_data.get(key)
    return None


def build_record(post, source_name):
    raw = post.raw_data or {}
    return LeakRecord(
        id=post.id,
        source_name=source_name,
        title=post.title,
        author=post.author,
        category=post.category,
        group=extract_from_raw(raw, "group"),
        country=extract_from_raw(raw, "country"),
        domain=extract_from_raw(raw, "domain"),
        published_at=post.published_at,
        victim_info=post.victim_info if isinstance(post.victim_info, dict) else None,
        screenshot=extract_from_raw(raw, "screenshot"),
    )


@router.post("", response_model=CheckResponse)
def check(req: CheckRequest, db: Session = Depends(get_db)):
    category = req.category.strip().lower()
    query = req.query.strip().lower() if req.query else ""

    base_query = db.query(Post, Source.name).join(Source, Post.source_id == Source.id)

    # query가 없으면 해당 카테고리 전체 조회
    if not query:
        if category == "group":
            results = (
                base_query.filter(Post.raw_data.cast(String).contains('"group"'))
                .order_by(Post.published_at.desc())
                .all()
            )
        elif category == "country":
            results = (
                base_query.filter(Post.raw_data.cast(String).contains('"country"'))
                .order_by(Post.published_at.desc())
                .all()
            )
        else:
            results = (
                base_query.order_by(Post.published_at.desc())
                .all()
            )
    elif category == "group":
        # author 필드 또는 raw_data.group에서 검색
        results = (
            base_query.filter(
                or_(
                    Post.author.contains(query),
                    Post.raw_data.cast(String).contains(query),
                )
            )
            .order_by(Post.published_at.desc())
            .all()
        )

    elif category == "country":
        # raw_data.country에서 검색 (KR, US, SE 등)
        results = (
            base_query.filter(
                Post.raw_data.cast(String).contains(query.upper())
            )
            .order_by(Post.published_at.desc())
            .all()
        )

    elif category == "victim_info":
        # victim_info, content, title, raw_data.domain에서 검색
        results = (
            base_query.filter(
                or_(
                    Post.title.contains(query),
                    Post.content.contains(query),
                    Post.raw_data.cast(String).contains(query),
                )
            )
            .order_by(Post.published_at.desc())
            .all()
        )

    elif category == "email":
        # 기존 이메일 검색 (하위 호환)
        results = (
            base_query.filter(
                or_(
                    Post.content.contains(query),
                    Post.raw_data.cast(String).contains(query),
                )
            )
            .order_by(Post.published_at.desc())
            .all()
        )
    else:
        # 전체 검색
        results = (
            base_query.filter(
                or_(
                    Post.title.contains(query),
                    Post.content.contains(query),
                    Post.author.contains(query),
                    Post.raw_data.cast(String).contains(query),
                )
            )
            .order_by(Post.published_at.desc())
            .all()
        )

    records = [build_record(post, source_name) for post, source_name in results]

    # 이메일 검색일 때만 크롤러 emails 테이블도 확인
    crawler_record = None
    if category == "email":
        try:
            crawler_email = db.query(CrawlerEmail).filter(CrawlerEmail.email == query).first()
            if crawler_email:
                domains = [d.netloc for d in crawler_email.domains]
                crawler_record = CrawlerRecord(email=query, found_on=domains)
        except Exception:
            pass

    total_count = len(records) + (1 if crawler_record else 0)

    return CheckResponse(
        category=category,
        query=query,
        is_leaked=total_count > 0,
        leak_count=total_count,
        records=records,
        crawler_results=crawler_record,
    )
