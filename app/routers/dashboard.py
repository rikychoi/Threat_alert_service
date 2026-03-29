# 대시보드 통계 - 프론트 대시보드 페이지에서 쓰는 데이터 전부 여기서 줌
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case

from app.database import get_db
from app.models.post import Post
from app.models.source import Source
from app.models.alert import Alert

router = APIRouter()


@router.get("")
def get_dashboard(db: Session = Depends(get_db)):
    """프론트 대시보드에 필요한 요약/시리즈/최근 목록 한 방에 반환"""
    now = datetime.now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    # 이번 주 월요일 0시
    monday = today - timedelta(days=today.weekday())

    # === summary ===
    total_posts = db.query(func.count(Post.id)).scalar() or 0
    active_sources = db.query(func.count(Source.id)).filter(Source.is_active == True).scalar() or 0
    new_posts_today = db.query(func.count(Post.id)).filter(Post.created_at >= today).scalar() or 0
    new_posts_this_week = db.query(func.count(Post.id)).filter(Post.created_at >= monday).scalar() or 0

    total_alerts = db.query(func.count(Alert.id)).scalar() or 0
    success_alerts = db.query(func.count(Alert.id)).filter(Alert.is_success == True).scalar() or 0
    alert_success_rate = round((success_alerts / total_alerts * 100), 1) if total_alerts > 0 else 0

    summary = {
        "total_posts": total_posts,
        "active_sources": active_sources,
        "new_posts_today": new_posts_today,
        "new_posts_this_week": new_posts_this_week,
        "alert_success_rate": alert_success_rate,
    }

    # === posts_by_month (최근 12개월) ===
    twelve_months_ago = now - relativedelta(months=11)
    start_month = twelve_months_ago.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # published_at 우선, 없으면 created_at
    date_col = func.coalesce(Post.published_at, Post.created_at)
    monthly_raw = (
        db.query(
            func.date_format(date_col, '%Y-%m').label('month_key'),
            func.count(Post.id),
        )
        .filter(date_col >= start_month)
        .group_by('month_key')
        .all()
    )
    monthly_map = {mk: cnt for mk, cnt in monthly_raw}

    posts_by_month = []
    for i in range(12):
        m = start_month + relativedelta(months=i)
        mk = m.strftime('%Y-%m')
        label = f"{m.year}년 {m.month}월"
        posts_by_month.append({
            "month_key": mk,
            "label": label,
            "count": monthly_map.get(mk, 0),
        })

    # === posts_by_category ===
    cat_rows = (
        db.query(Post.category, func.count(Post.id))
        .group_by(Post.category)
        .all()
    )
    posts_by_category = [
        {"category": cat or "미분류", "count": cnt}
        for cat, cnt in cat_rows
    ]

    # === top_sources (상위 10개) ===
    src_rows = (
        db.query(Source.name, func.count(Post.id))
        .join(Post, Post.source_id == Source.id)
        .group_by(Source.name)
        .order_by(func.count(Post.id).desc())
        .limit(10)
        .all()
    )
    top_sources = [{"name": name, "count": cnt} for name, cnt in src_rows]

    # === posts_by_site_type ===
    site_rows = (
        db.query(Source.site_type, func.count(Post.id))
        .join(Post, Post.source_id == Source.id)
        .group_by(Source.site_type)
        .all()
    )
    posts_by_site_type = [{"site_type": st, "count": cnt} for st, cnt in site_rows]

    # === alerts_by_channel ===
    channel_rows = (
        db.query(Alert.channel, func.count(Alert.id))
        .group_by(Alert.channel)
        .all()
    )
    alerts_by_channel = [{"channel": ch, "count": cnt} for ch, cnt in channel_rows]

    # === alert_outcomes ===
    alert_outcomes = {
        "success": success_alerts,
        "failure": total_alerts - success_alerts,
    }

    # === recent_posts (최근 20건) ===
    recent_post_rows = (
        db.query(Post)
        .order_by(Post.created_at.desc())
        .limit(20)
        .all()
    )
    recent_posts = [
        {
            "id": p.id,
            "title": p.title,
            "category": p.category,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
        for p in recent_post_rows
    ]

    # === recent_alerts (최근 20건) ===
    recent_alert_rows = (
        db.query(Alert)
        .order_by(Alert.sent_at.desc())
        .limit(20)
        .all()
    )
    recent_alerts = [
        {
            "id": a.id,
            "channel": a.channel,
            "is_success": a.is_success,
            "sent_at": a.sent_at.isoformat() if a.sent_at else None,
        }
        for a in recent_alert_rows
    ]

    return {
        "summary": summary,
        "posts_by_month": posts_by_month,
        "posts_by_category": posts_by_category,
        "top_sources": top_sources,
        "posts_by_site_type": posts_by_site_type,
        "alerts_by_channel": alerts_by_channel,
        "alert_outcomes": alert_outcomes,
        "recent_posts": recent_posts,
        "recent_alerts": recent_alerts,
    }


# 기존 API도 유지 (하위 호환)
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
