# 프론트 드롭다운에 보여줄 검색 카테고리 목록
from fastapi import APIRouter

router = APIRouter()


@router.get("")
def get_categories():
    return ["group", "country", "victim_info", "email"]
