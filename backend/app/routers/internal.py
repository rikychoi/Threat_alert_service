# 크롤러/파서에서 데이터 넘겨받는 내부 API - 외부 노출 X
# 게시물 저장되면 알림도 자동으로 쏴줌
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.post import Post
from app.models.alert import Alert
from app.schemas.post import PostCreate, PostResponse
from app.services.alert_service import send_slack_alert, send_discord_alert

logger = logging.getLogger(__name__)

router = APIRouter()


def _send_alerts(post: Post, db: Session):
    """게시물 저장 후 슬랙/디스코드 알림 발송 + alerts 테이블에 기록"""
    detail_url = f"/api/posts/{post.id}"

    # 슬랙 알림
    slack_ok = send_slack_alert(
        title=post.title,
        author=post.author or "unknown",
        category=post.category,
        url=detail_url,
    )
    if slack_ok:
        db.add(Alert(
            post_id=post.id,
            channel="slack",
            message=f"[신규 유출 탐지] {post.title}",
            is_success=True,
        ))
        logger.info(f"슬랙 알림 발송 완료: {post.title}")

    # 디스코드 알림
    discord_ok = send_discord_alert(
        title=post.title,
        author=post.author or "unknown",
        category=post.category,
        url=detail_url,
    )
    if discord_ok:
        db.add(Alert(
            post_id=post.id,
            channel="discord",
            message=f"[신규 유출 탐지] {post.title}",
            is_success=True,
        ))
        logger.info(f"디스코드 알림 발송 완료: {post.title}")

    db.commit()


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

    # 저장 성공하면 알림 자동 발송
    try:
        _send_alerts(post, db)
    except Exception as e:
        logger.error(f"알림 발송 실패 (게시물은 저장됨): {e}")

    return post
