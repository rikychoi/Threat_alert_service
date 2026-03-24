#게시물 목록이랑 상세 조회 - 대시보드에서 쓸 API
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.post import Post
from app.schemas.post import PostResponse, PostListResponse

router = APIRouter()


@router.get("", response_model=PostListResponse)
def get_posts(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Post)

    if category:
        query = query.filter(Post.category == category)
    if search:
        query = query.filter(Post.title.contains(search) | Post.content.contains(search))

    total = query.count()
    items = query.order_by(desc(Post.created_at)).offset((page - 1) * size).limit(size).all()

    return PostListResponse(total=total, page=page, size=size, items=items)


@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시물을 찾을 수 없습니다")
    return post
