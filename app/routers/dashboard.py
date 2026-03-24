# 대시보드 통계 - 오늘 몇건 들어왔는지, 카테고리별 현황 등
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.post import Post
from app.models.alert import Alert

router = APIRouter()


@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    total_posts = db.query(func.count(Post.id)).scalar()
    today_posts = db.query(func.count(Post.id)).filter(Post.created_at >= today).scalar()
    total_alerts = db.query(func.count(Alert.id)).scalar()

    category_stats = (
        db.query(Post.category, func.count(Post.id))
        .group_by(Post.category)
        .all()
    )

    return {
        "total_posts": total_posts,
        "today_posts": today_posts,
        "total_alerts": total_alerts,
        "category_stats": {cat: count for cat, count in category_stats},
    }


@router.get("/timeline")
def get_timeline(days: int = 30, db: Session = Depends(get_db)):
    since = datetime.now() - timedelta(days=days)

    daily_counts = (
        db.query(func.date(Post.created_at), func.count(Post.id))
        .filter(Post.created_at >= since)
        .group_by(func.date(Post.created_at))
        .order_by(func.date(Post.created_at))
        .all()
    )

    return [{"date": str(date), "count": count} for date, count in daily_counts]
