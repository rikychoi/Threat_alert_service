#Sentinel 백엔드 서버 진입점 - 여기서 라우터 등록하고 CORS 세팅함
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from app.models import base
from app.routers import check, posts, dashboard, internal, categories, sources


base.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sentinel API",
    description="다크웹 유출 정보 조회 및 모니터링 API",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # React 개발 서버
        "http://127.0.0.1:3000",
        "*",                           
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(check.router, prefix="/api/check", tags=["유출 조회"])
app.include_router(categories.router, prefix="/api/categories", tags=["카테고리"])
app.include_router(posts.router, prefix="/api/posts", tags=["게시물"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["대시보드"])
app.include_router(sources.router, prefix="/api/sources", tags=["소스 관리"])
app.include_router(internal.router, prefix="/api/internal", tags=["내부용"])


@app.get("/")
def health_check():
    return {"status": "ok", "service": "Sentinel API"}
