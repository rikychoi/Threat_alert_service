# 크롤링 대상 사이트 관리 - 추가/수정/삭제/목록 다 여기서 처리
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.source import Source
from app.schemas.source import SourceCreate, SourceUpdate, SourceResponse

router = APIRouter()


@router.get("", response_model=List[SourceResponse])
def list_sources(db: Session = Depends(get_db)):
    """전체 소스 목록 - is_active 상관없이 다 보여줌"""
    return db.query(Source).order_by(Source.created_at.desc()).all()


@router.get("/{source_id}", response_model=SourceResponse)
def get_source(source_id: int, db: Session = Depends(get_db)):
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="소스를 찾을 수 없습니다")
    return source


@router.post("", response_model=SourceResponse, status_code=201)
def create_source(data: SourceCreate, db: Session = Depends(get_db)):
    """새 크롤링 대상 사이트 추가"""
    source = Source(
        name=data.name,
        url=data.url,
        site_type=data.site_type,
        description=data.description,
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


@router.put("/{source_id}", response_model=SourceResponse)
def update_source(source_id: int, data: SourceUpdate, db: Session = Depends(get_db)):
    """소스 정보 수정 - 보낸 필드만 업데이트됨"""
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="소스를 찾을 수 없습니다")

    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(source, key, value)

    db.commit()
    db.refresh(source)
    return source


@router.delete("/{source_id}")
def delete_source(source_id: int, db: Session = Depends(get_db)):
    """소스 삭제 - 연결된 posts가 있으면 못 지움"""
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="소스를 찾을 수 없습니다")

    try:
        db.delete(source)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=409, detail="이 소스에 연결된 게시물이 있어서 삭제할 수 없습니다")

    return {"detail": "삭제 완료"}
