# Sentinel DB-Backend

다크웹 유출 정보 조회 및 모니터링 API 서버

## 기술 스택

- Python 3.9+
- FastAPI
- SQLAlchemy (ORM)
- MySQL 8.0 / MariaDB
- PyMySQL

## 프로젝트 구조

```
db-backend/
├── app/
│   ├── main.py            # 서버 진입점
│   ├── config.py          # DB, 알림 설정
│   ├── database.py        # DB 연결
│   ├── models/            # 테이블 정의 (ORM)
│   │   ├── source.py      # 크롤링 대상 사이트
│   │   ├── post.py        # 수집된 게시물
│   │   └── alert.py       # 알림 발송 기록
│   ├── schemas/           # 요청/응답 형식
│   │   ├── post.py        # 게시물 관련
│   │   └── check.py       # 이메일 유출 조회
│   ├── routers/           # API 엔드포인트
│   │   ├── check.py       # 이메일 유출 조회
│   │   ├── posts.py       # 게시물 목록/상세
│   │   ├── dashboard.py   # 대시보드 통계
│   │   └── internal.py    # 크롤러 데이터 수신
│   └── services/
│       └── alert_service.py  # Slack/Discord 알림
├── sql/
│   └── schema.sql         # 테이블 생성 + 테스트 데이터
├── requirements.txt
├── .env.example
└── .gitignore
```

## 로컬 환경 세팅

### 1. MySQL 설치 및 시작

```bash
# Mac (Homebrew)
brew install mysql
brew services start mysql
-> 윈도우는 제가 사용을 잘 안해서 직접 서칭 한번 해보셔야 할거 같습니다 ㅠㅠ
```

### 2. DB 생성

```bash
mysql -u root < sql/schema.sql
```

잘 들어갔는지 확인하려면:

```bash
mysql -u root -e "USE darkweb_monitor; SHOW TABLES;"
```

아래처럼 나오면 정상:

```
Tables_in_darkweb_monitor
alerts
posts
sources
```

### 3. 패키지 설치

```bash
pip install -r requirements.txt
```

### 4. 환경변수 설정

```bash
cp .env.example .env
```

`.env` 파일 열어서 본인 DB 비밀번호 넣기 (brew로 깔았으면 비밀번호 없으니 그냥 둬도 됨)

### 5. 서버 실행

```bash
uvicorn app.main:app --reload --port 8000
```

실행되면 터미널에 아래 메시지 뜸:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 6. 확인

- 브라우저에서 http://localhost:8000 접속 → `{"status":"ok","service":"Sentinel API"}` 나오면 성공
- http://localhost:8000/docs → Swagger UI에서 모든 API 테스트 가능

## API 목록

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/api/check` | 이메일 유출 여부 조회 (프론트 연동) |
| GET | `/api/posts` | 게시물 목록 (페이지네이션, 검색) |
| GET | `/api/posts/{id}` | 게시물 상세 |
| GET | `/api/dashboard/summary` | 대시보드 요약 통계 |
| GET | `/api/dashboard/timeline` | 일별 게시물 추이 |
| POST | `/api/internal/posts` | 크롤러 데이터 저장 (내부용) |

## API 테스트 방법

### 이메일 유출 조회

```bash
curl -X POST http://localhost:8000/api/check \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com"}'
```

유출된 이메일이면:

```json
{
  "email": "test@example.com",
  "is_leaked": true,
  "leak_count": 2,
  "records": [...]
}
```

유출 안 된 이메일이면:

```json
{
  "email": "safe@gmail.com",
  "is_leaked": false,
  "leak_count": 0,
  "records": []
}
```

### 게시물 목록 조회

```bash
# 전체 조회
curl http://localhost:8000/api/posts

# 카테고리 필터
curl "http://localhost:8000/api/posts?category=leak_data"

# 키워드 검색
curl "http://localhost:8000/api/posts?search=Company"
```

### 대시보드 통계

```bash
curl http://localhost:8000/api/dashboard/summary
```

### 게시물 저장 (크롤러/파서용)

```bash
curl -X POST http://localhost:8000/api/internal/posts \
  -H "Content-Type: application/json" \
  -d '{
    "source_id": 1,
    "title": "Test Leak Data",
    "author": "hacker123",
    "content": "leaked emails: someone@test.com",
    "content_hash": "아무고유값넣으면됨",
    "category": "leak_data"
  }'
  -> 터미널에서 직접 실행하는 방법
```

## DB 스키마

테이블 3개:

- `sources` - 크롤링 대상 사이트 (BreachForums, LockBit 등)
- `posts` - 수집된 게시물 (핵심 테이블)
- `alerts` - 알림 발송 기록

ERD는 `docs/erd.dbml` 파일을 [dbdiagram.io](https://dbdiagram.io)에 붙여넣으면 볼 수 있음

## 프론트엔드 연동

프론트(React)에서 이메일 조회할 때:

```javascript
const res = await fetch('http://localhost:8000/api/check', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: '조회할이메일@example.com' }),
});
const data = await res.json();
// data.is_leaked → true/false
// data.leak_count → 유출 건수
// data.records → 유출 상세 목록
```

CORS 설정 되어있어서 `localhost:3000` (React 개발서버)에서 바로 호출 가능
