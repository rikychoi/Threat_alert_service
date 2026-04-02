# 게시물 목록이랑 상세 조회 - 대시보드에서 쓸 API
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.post import Post
from app.schemas.post import PostResponse, PostListResponse

router = APIRouter()


def post_to_response(post) -> dict:
    """raw_data에서 group/country/domain/screenshot 꺼내서 응답에 포함"""
    raw = post.raw_data if isinstance(post.raw_data, dict) else {}
    return {
        "id": post.id,
        "source_id": post.source_id,
        "title": post.title,
        "author": post.author,
        "content": post.content,
        "published_at": post.published_at,
        "category": post.category,
        "tags": post.tags,
        "victim_info": post.victim_info if isinstance(post.victim_info, dict) else None,
        "original_url": post.original_url,
        "group": raw.get("group"),
        "country": raw.get("country"),
        "domain": raw.get("domain"),
        "screenshot": raw.get("screenshot"),
        "created_at": post.created_at,
    }


@router.get("", response_model=PostListResponse)
def get_posts(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    search: Optional[str] = None,
    group: Optional[str] = None,
    country: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Post)

    if category:
        query = query.filter(Post.category == category)
    if search:
        query = query.filter(Post.title.contains(search) | Post.content.contains(search))
    if group:
        query = query.filter(Post.author == group)

    total = query.count()
    posts = query.order_by(desc(Post.created_at)).offset((page - 1) * size).limit(size).all()

    items = [PostResponse(**post_to_response(p)) for p in posts]
    return PostListResponse(total=total, page=page, size=size, items=items)


@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시물을 찾을 수 없습니다")
    return PostResponse(**post_to_response(post))
