# OpenNaru 위키 엔진

미디어위키와 나무위키(더 시드)의 장점만을 결합한 차세대 오픈소스 위키 엔진입니다.

나무마크 호환 문법, 현대적인 UI/UX, 강력한 틀(Template) 시스템, 멀티위키 지원을 하나의 엔진에서 제공합니다.

---

## 주요 특징

- **나무마크 확장 문법** — 나무위키 사용자에게 익숙한 문법 + 마크다운 코드 블록 + KaTeX 수식
- **WYSIWYG 에디터** — 문법을 몰라도 편집 가능
- **틀(Template) 시스템** — 재사용 가능한 정보상자, 반복 구조 (미디어위키 수준)
- **멀티위키 지원** — 하나의 설치로 N개의 독립 위키 운영
- **문서별 ACL 권한** — 읽기/편집 권한을 문서 단위로 세밀하게 설정
- **완전한 편집 이력 보존** — 모든 버전 비교, 롤백, 이력 말소
- **AI 문서 요약** — 문서 상단에 자동 요약 표시
- **실시간 미리보기** — 편집 중 렌더링 결과 즉시 확인
- **PostgreSQL / MySQL / SQLite 지원**

---

## 기술 스택

| 구분 | 기술 |
|------|------|
| 백엔드 | Python 3.11+ / FastAPI / SQLAlchemy |
| 프론트엔드 | TypeScript / Next.js 14 / Tailwind CSS |
| DB | PostgreSQL 15+ (기본) / MySQL 8+ / SQLite |
| 검색 | Meilisearch (선택) / PostgreSQL FTS |
| 캐시 | Redis |
| 인프라 | Docker / Nginx |

---

## 빠른 시작 (Docker)

```bash
# 1. 저장소 클론
git clone https://github.com/LeeJuhyeong424/OpenNaru.git
cd OpenNaru

# 2. 환경변수 설정
cp .env.example .env
# .env 파일에서 APP_SECRET_KEY 값 변경 (필수)

# 3. 실행
docker compose up -d

# 4. DB 초기화
docker compose exec backend alembic upgrade head

# 5. 브라우저에서 http://localhost:3000 접속
```

## 로컬 개발 환경

```bash
# 백엔드
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
cp ../.env.example .env
uvicorn app.main:app --reload   # http://localhost:8000

# 프론트엔드
cd frontend
npm install
npm run dev   # http://localhost:3000
```

---

## 문서

| 문서 | 설명 |
|------|------|
| [개발 환경 세팅](docs/getting-started.md) | 로컬·Docker 개발 환경 구성 |
| [기여자 가이드](docs/contributing.md) | 브랜치 전략, 커밋 컨벤션, PR 규칙 |
| [배포 가이드](docs/deployment.md) | Docker Compose·Kubernetes 프로덕션 배포 |
| [파서 설계](docs/parser-design.md) | 나무마크 파서 아키텍처 |

---

## 기여 방법

1. 이 저장소를 Fork 합니다
2. `feat/기능명` 또는 `fix/버그명` 브랜치를 생성합니다
3. 변경 사항을 작성하고 테스트를 통과시킵니다
4. [Conventional Commits](https://www.conventionalcommits.org/) 형식에 맞게 커밋합니다
5. Pull Request를 제출합니다

---

## 라이선스

MIT License — 자세한 내용은 [LICENSE](LICENSE) 파일을 참고해주세요.
