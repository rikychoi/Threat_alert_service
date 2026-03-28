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
│   │   ├── alert.py       # 알림 발송 기록
│   │   └── crawler_models.py  # 크롤러 DB 테이블 (읽기 전용)
│   ├── schemas/           # 요청/응답 형식
│   │   ├── post.py        # 게시물 관련
│   │   ├── check.py       # 유출 조회 (카테고리별)
│   │   └── source.py      # 소스 CRUD
│   ├── routers/           # API 엔드포인트
│   │   ├── check.py       # 유출 조회 (그룹/국가/피해자/이메일)
│   │   ├── categories.py  # 검색 카테고리 목록
│   │   ├── posts.py       # 게시물 목록/상세
│   │   ├── sources.py     # 크롤링 소스 관리 (CRUD)
│   │   ├── dashboard.py   # 대시보드 통계
│   │   └── internal.py    # 크롤러 데이터 수신 + 알림 자동 발송
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
address_identifier
addresses
alerts
domains
email_identifier
emails
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

알림 보내려면 Slack/Discord 웹훅 URL도 넣으면 됨 (없으면 알림만 안 가고 나머지는 정상 동작)

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
| POST | `/api/check` | 유출 조회 - 카테고리별 검색 (그룹/국가/피해자/이메일) |
| GET | `/api/categories` | 검색 카테고리 목록 (프론트 드롭다운용) |
| GET | `/api/posts` | 게시물 목록 (페이지네이션, 검색, 필터) |
| GET | `/api/posts/{id}` | 게시물 상세 |
| GET | `/api/sources` | 크롤링 소스 목록 |
| GET | `/api/sources/{id}` | 소스 상세 |
| POST | `/api/sources` | 소스 추가 |
| PUT | `/api/sources/{id}` | 소스 수정 |
| DELETE | `/api/sources/{id}` | 소스 삭제 |
| GET | `/api/dashboard/summary` | 대시보드 요약 통계 |
| GET | `/api/dashboard/timeline` | 일별 게시물 추이 |
| POST | `/api/internal/posts` | 크롤러 데이터 저장 + 알림 자동 발송 (내부용) |

## API 테스트 방법

### 유출 조회 (카테고리별 검색)

```bash
# 그룹으로 검색
curl -X POST http://localhost:8000/api/check \
  -H "Content-Type: application/json" \
  -d '{"category":"group","query":"lockbit"}'

# 국가로 검색
curl -X POST http://localhost:8000/api/check \
  -H "Content-Type: application/json" \
  -d '{"category":"country","query":"KR"}'

# 피해자 정보로 검색
curl -X POST http://localhost:8000/api/check \
  -H "Content-Type: application/json" \
  -d '{"category":"victim_info","query":"knuh.kr"}'

# 이메일로 검색 (크롤러 DB도 같이 조회)
curl -X POST http://localhost:8000/api/check \
  -H "Content-Type: application/json" \
  -d '{"category":"email","query":"test@example.com"}'

# 카테고리만 선택하고 query 없이 보내면 해당 카테고리 전체 조회
curl -X POST http://localhost:8000/api/check \
  -H "Content-Type: application/json" \
  -d '{"category":"group"}'
```

유출이 감지되면:

```json
{
  "category": "group",
  "query": "lockbit",
  "is_leaked": true,
  "leak_count": 1,
  "records": [
    {
      "id": 3,
      "source_name": "RansomwareLive",
      "title": "Korean National University Hospital",
      "author": "lockbit",
      "category": "ransomware",
      "group": "lockbit",
      "country": "KR",
      "domain": "knuh.kr",
      "published_at": "2026-03-21T14:00:00",
      "victim_info": {"domain": "knuh.kr"},
      "screenshot": "https://images.ransomware.live/..."
    }
  ],
  "crawler_results": null
}
```

이메일 검색 시 크롤러 DB에서도 찾으면:

```json
{
  "category": "email",
  "query": "test@example.com",
  "is_leaked": true,
  "leak_count": 4,
  "records": [...],
  "crawler_results": {
    "email": "test@example.com",
    "found_on": ["breachforum1234.onion", "darkmarket5678.onion"]
  }
}
```

### 게시물 목록 조회

```bash
# 전체 조회
curl http://localhost:8000/api/posts

# 카테고리 필터
curl "http://localhost:8000/api/posts?category=ransomware"

# 그룹 필터
curl "http://localhost:8000/api/posts?group=lockbit"

# 키워드 검색
curl "http://localhost:8000/api/posts?search=Hospital"
```

### 소스 관리

```bash
# 목록
curl http://localhost:8000/api/sources

# 추가
curl -X POST http://localhost:8000/api/sources \
  -H "Content-Type: application/json" \
  -d '{"name":"New Forum","url":"http://newforum.onion","site_type":"forum"}'

# 수정
curl -X PUT http://localhost:8000/api/sources/1 \
  -H "Content-Type: application/json" \
  -d '{"description":"설명 변경"}'

# 삭제 (연결된 게시물 있으면 삭제 안 됨)
curl -X DELETE http://localhost:8000/api/sources/4
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
    "category": "leak_data",
    "raw_data": {"group": "hacker123", "country": "KR", "domain": "test.kr"}
  }'
-> 저장되면 Slack/Discord 웹훅 설정되어있으면 알림도 자동으로 감
```

## DB 스키마

테이블 8개:

**메인 테이블**
- `sources` - 크롤링 대상 사이트 (BreachForums, LockBit Blog 등)
- `posts` - 수집된 게시물 (핵심 테이블, raw_data에 group/country/domain/screenshot 들어있음)
- `alerts` - 알림 발송 기록 (슬랙/디스코드)

**크롤러 테이블**
- `domains` - 크롤러가 발견한 .onion 도메인
- `emails` - 크롤러가 발견한 이메일 주소
- `addresses` - 크롤러가 발견한 암호화폐 주소
- `email_identifier` - 이메일-도메인 연결 (M:N)
- `address_identifier` - 주소-도메인 연결 (M:N)

ERD는 `docs/erd.dbml` 파일을 [dbdiagram.io](https://dbdiagram.io)에 붙여넣으면 볼 수 있음

## 프론트엔드 연동

프론트(React)에서 유출 조회할 때:

```javascript
// 카테고리 목록 가져오기 (드롭다운용)
const categories = await fetch('http://localhost:8000/api/categories').then(r => r.json());
// → ["group", "country", "victim_info", "email"]

// 유출 조회
const res = await fetch('http://localhost:8000/api/check', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ category: 'group', query: 'lockbit' }),
});
const data = await res.json();
// data.is_leaked → true/false
// data.leak_count → 유출 건수
// data.records → 유출 상세 목록
// data.crawler_results → 크롤러 이메일 검색 결과 (이메일 검색 시)
```

CORS 설정 되어있어서 `localhost:3000` (React 개발서버)에서 바로 호출 가능

## 알림 설정

`.env`에 웹훅 URL 넣으면 게시물 저장 시 자동 알림 발송됨:

```
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx/yyy/zzz
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/xxx/yyy
```

설정 안 하면 알림만 안 가고 나머지는 정상 동작함
