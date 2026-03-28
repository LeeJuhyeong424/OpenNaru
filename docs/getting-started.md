# 개발 환경 세팅 가이드

## 사전 요구사항

| 도구 | 최소 버전 |
|------|-----------|
| Python | 3.11+ |
| Node.js | 20 LTS+ |
| PostgreSQL | 15+ |
| Redis | 7+ |
| Docker (선택) | 24+ |
| Git | 2.40+ |

## 방식 A — Docker Compose (권장)

```bash
git clone https://github.com/LeeJuhyeong424/OpenNaru.git
cd OpenNaru
cp .env.example .env
# .env에서 APP_SECRET_KEY 필수 변경

docker compose up -d
docker compose exec backend alembic upgrade head
# http://localhost:3000
```

## 방식 B — 로컬 직접 설치

### 백엔드 (Python)

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements-dev.txt
cp ../.env.example .env
uvicorn app.main:app --reload   # http://localhost:8000
```

### 프론트엔드 (Node.js)

```bash
cd frontend
npm install
npm run dev   # http://localhost:3000
```

### PostgreSQL

```bash
# 데이터베이스 생성
psql -U postgres -c "CREATE DATABASE opennaru;"
psql -U postgres -c "CREATE USER opennaru WITH PASSWORD 'yourpassword';"
psql -U postgres -c "GRANT ALL ON DATABASE opennaru TO opennaru;"

# .env에서 DATABASE_URL 설정
# DATABASE_URL=postgresql://opennaru:yourpassword@localhost:5432/opennaru

# 마이그레이션
cd backend
alembic upgrade head
```

## 환경변수 (.env) 설정

`.env.example` 을 복사하여 `.env` 를 만들고 필요한 값을 채웁니다.

| 변수 | 설명 | 필수 |
|------|------|------|
| `APP_SECRET_KEY` | JWT 서명 비밀키 (32자 이상 랜덤 문자열) | ✅ |
| `DATABASE_URL` | PostgreSQL 연결 URL | ✅ |
| `CORS_ORIGINS` | 허용할 프론트엔드 URL | ✅ |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access Token 만료 시간 (기본: 60) | |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh Token 만료 시간 (기본: 14) | |
| `REDIS_URL` | Redis 연결 URL | |

## VS Code 추천 익스텐션

- **Python** (ms-python.python)
- **Pylance** (ms-python.vscode-pylance)
- **Ruff** (charliermarsh.ruff) — 린터/포매터
- **ESLint** (dbaeumer.vscode-eslint)
- **Prettier** (esbenp.prettier-vscode)
- **Tailwind CSS IntelliSense** (bradlc.vscode-tailwindcss)

## Git 브랜치 전략

```
main      — 프로덕션 릴리스 태그
develop   — 통합 브랜치 (기본 작업 브랜치)
feat/*    — 새 기능
fix/*     — 버그 수정
docs/*    — 문서만 변경
refactor/* — 리팩토링
```

## 커밋 메시지 컨벤션

[Conventional Commits](https://www.conventionalcommits.org/) 규격을 따릅니다.

```
feat: 사용자 로그인 API 구현
fix: 파서 XSS 이스케이프 누락 수정
docs: 배포 가이드 초안 작성
refactor: 인라인 파서 재귀 구조 개선
test: 표 파싱 테스트 추가
chore: 의존성 업데이트
```

## 유용한 명령어

```bash
# 백엔드 테스트 실행
cd backend && pytest

# 단일 테스트 파일
pytest tests/test_parser.py -v

# 린트
cd backend && ruff check .
cd frontend && npm run lint

# DB 마이그레이션 생성
cd backend && alembic revision --autogenerate -m "설명"

# 마이그레이션 적용
cd backend && alembic upgrade head
```
