#이메일 유출 조회 - 프론트에서 이메일 넣으면 여기서 DB 뒤져서 결과 돌려줌
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models.post import Post
from app.models.source import Source
from app.schemas.check import EmailCheckRequest, EmailCheckResponse, LeakRecord

router = APIRouter()


@router.post("", response_model=EmailCheckResponse)
def check_email(req: EmailCheckRequest, db: Session = Depends(get_db)):
    email = req.email.strip().lower()

    results = (
        db.query(Post, Source.name)
        .join(Source, Post.source_id == Source.id)
        .filter(
            or_(
                Post.content.contains(email),
                Post.raw_data.cast(String).contains(email),
            )
        )
        .order_by(Post.published_at.desc())
        .all()
    )

    records = []
    for post, source_name in results:
        records.append(LeakRecord(
            id=post.id,
            source_name=source_name,
            title=post.title,
            category=post.category,
            published_at=post.published_at,
            victim_info=post.victim_info,
        ))

    return EmailCheckResponse(
        email=email,
        is_leaked=len(records) > 0,
        leak_count=len(records),
        records=records,
    )


from sqlalchemy import String
