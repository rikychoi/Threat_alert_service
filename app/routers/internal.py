# 크롤러/파서에서 데이터 넘겨받는 내부 API - 외부 노출 X
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.post import Post
from app.schemas.post import PostCreate, PostResponse

router = APIRouter()


@router.post("/posts", response_model=PostResponse)
def create_post(data: PostCreate, db: Session = Depends(get_db)):
    post = Post(
        source_id=data.source_id,
        title=data.title,
        author=data.author,
        content=data.content,
        published_at=data.published_at,
        content_hash=data.content_hash,
        category=data.category,
        tags=data.tags,
        victim_info=data.victim_info,
        original_url=data.original_url,
        raw_data=data.raw_data,
    )

    try:
        db.add(post)
        db.commit()
        db.refresh(post)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="이미 저장된 게시물입니다 (content_hash 중복)")

    return post
