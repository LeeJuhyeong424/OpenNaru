# CLAUDE.md — OpenNaru

> **팀 AI 운영 지침 포함** | 혼자 개발 + Claude Code 에이전트 분업 구조

---

## 🤖 팀 AI 에이전트 구성 (Claude Code)

이 프로젝트는 **오케스트레이터 1 + 전문 에이전트 4** 구조로 운영한다.
각 에이전트는 자신의 담당 영역 외 코드를 **직접 수정하지 않고** 오케스트레이터에게 위임한다.

| 에이전트 | 담당 영역 | 주요 파일 |
|----------|----------|-----------|
| **오케스트레이터** | 태스크 분배, 충돌 조율, 통합 | `CLAUDE.md`, `doc/` |
| **파서 에이전트** | 나무마크 파서 전담 | `backend/app/parser/` |
| **백엔드 에이전트** | FastAPI, DB, API, 서비스 레이어 | `backend/app/` (parser 제외) |
| **프론트엔드 에이전트** | Next.js, UI 컴포넌트, API 연동 | `frontend/` |
| **QA 에이전트** | 테스트 작성, ACL 검증, 보안 리뷰 | `backend/tests/` |

### 에이전트 공통 규칙
- 작업 시작 전 이 파일(CLAUDE.md) 전체를 읽는다
- 담당 외 영역 수정이 필요하면 TODO 주석으로 남기고 오케스트레이터에게 보고
- 인터페이스(API 스펙, 스키마, 파서 출력 형식) 변경 시 반드시 오케스트레이터 승인 후 진행

---

## 언어 규칙

- **응답**: 항상 한국어로 답변
- **코드 주석**: 한국어
- **커밋 메시지**: 한국어 (Conventional Commits 형식 준수)
- **문서**: 한국어
- **변수/함수/클래스명**: 영어 (코드 표준 준수)

커밋 메시지 예시:
```
feat(parser): 나무마크 굵기/기울임 문법 파싱 구현
fix(auth): JWT 만료 시 리다이렉트 오류 수정
docs(api): 문서 생성 API 응답 예시 추가
```
타입: `feat` / `fix` / `docs` / `refactor` / `test` / `chore` / `perf`

---

## 프로젝트 개요

**OpenNaru** — 미디어위키와 나무위키(더 시드)의 장점을 결합한 차세대 오픈소스 위키 엔진.
나무마크 확장 문법, WYSIWYG 에디터, 미디어위키 수준의 틀 시스템, 멀티위키 지원, ACL 권한 체계를 하나의 엔진으로 제공한다.

현재 단계: **Phase 1 — MVP 개발 중** (파서, 문서 CRUD, ACL, 검색, 기본 UI)

---

## 기술 스택

| 구분 | 기술 |
|------|------|
| 백엔드 | Python 3.14 / FastAPI / SQLAlchemy 2.x / Alembic |
| 프론트엔드 | TypeScript / Next.js 14+ / Tailwind CSS |
| DB | PostgreSQL (기본) / MySQL 8+ / SQLite 호환 |
| 검색 | Meilisearch (선택) / PostgreSQL FTS |
| 캐시 | Redis (추후 도입) |
| 개발 환경 | Windows + Python venv (Docker 미사용) |

---

## 개발 환경 실행

### 백엔드

```bash
cd backend

# 가상환경 활성화 (Windows)
.venv\Scripts\activate

# 개발 서버 (자동 재시작)
uvicorn app.main:app --reload

# 테스트 실행
pytest

# 단일 테스트 파일 실행
pytest tests/test_health.py -v

# 린트
ruff check .
```

### 프론트엔드

```bash
cd frontend
npm run dev    # 개발 서버 (http://localhost:3000)
npm run build  # 프로덕션 빌드
```

### DB 마이그레이션

```bash
cd backend

# 마이그레이션 파일 생성
alembic revision --autogenerate -m "설명"

# 마이그레이션 적용
alembic upgrade head

# 한 단계 롤백
alembic downgrade -1
```

---

## 디렉토리 구조

```
OpenNaru/
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── endpoints/   # 라우터 (auth.py, wikis.py, pages.py 등)
│   │   │   └── router.py    # 전체 라우터 등록
│   │   ├── core/
│   │   │   ├── config.py    # 환경변수 설정 (pydantic-settings)
│   │   │   └── database.py  # SQLAlchemy 엔진 / 세션 / Base
│   │   ├── models/          # SQLAlchemy ORM 모델
│   │   ├── schemas/         # Pydantic 요청/응답 스키마
│   │   ├── services/        # 비즈니스 로직 (라우터에서 직접 DB 접근 금지)
│   │   ├── parser/          # 나무마크 파서 (핵심 컴포넌트) ← 파서 에이전트 전담
│   │   └── main.py          # FastAPI 앱 진입점
│   ├── alembic/             # DB 마이그레이션
│   ├── tests/               # pytest 테스트
│   ├── .env                 # 환경변수 (Git 제외)
│   ├── requirements.txt
│   └── requirements-dev.txt
├── frontend/
│   └── src/
│       ├── app/             # Next.js App Router
│       ├── components/      # 공통 컴포넌트
│       ├── lib/             # API 클라이언트, 유틸
│       └── styles/
├── doc/                     # 설계 문서 (기획서, API 설계, DB 스키마 등)
└── .env.example
```

---

## 아키텍처 핵심 설계

### API 규칙

- 모든 엔드포인트: `/api/v1/` 접두사
- URL 패턴: `/api/v1/wikis/{wikiSlug}/pages/{pageSlug}`
- 응답: 항상 JSON, 오류 시 `{ code, message, detail }` 형태
- 인증: JWT Bearer (`Authorization: Bearer {token}`)
  - Access Token: 1시간 / Refresh Token: 14일
- 비인증 접근: 위키 설정(`default_edit_acl`)에 따라 비로그인 편집 허용 가능
- **없는 문서 조회 시**: 404 + `{ exists: false, can_create: true }` 반환 (나무위키 방식)

### ACL 권한 체계

> ⚠️ **모든 에이전트 필독** — 권한 로직은 반드시 서버 사이드에서만 처리한다.

등급 순서 (낮음 → 높음):
```
blocked → anonymous → member → autoconf → admin → sysadmin
```

적용 우선순위: **문서 ACL > 네임스페이스 ACL > 위키 기본값**

기본 정책: **비로그인(anonymous)도 편집 가능** (나무위키/미디어위키와 동일 철학).
프론트엔드에서 버튼을 숨기는 것은 UX 목적이지 보안이 아니다.

네임스페이스별 기본 편집 권한:
| 네임스페이스 | 기본 편집 | 이유 |
|-------------|----------|------|
| `main` | anonymous | 가장 개방적 |
| `talk` | anonymous | 누구나 토론 참여 |
| `user` | member | 본인 사용자 문서 |
| `template` | autoconf | 대량 영향 방지 |
| `file` | member | 파일 문서 |
| `help` | admin | 공식 도움말 |

### 나무마크 파서 파이프라인 (`app/parser/`)

> ⚠️ **파서 에이전트 전담 영역** — 다른 에이전트는 파서 내부를 직접 수정하지 않는다.
> 파서 수정이 필요하면 파서 에이전트에게 위임하거나 TODO로 남긴다.

4단계 처리:
1. **토크나이저** — 줄 단위로 토큰 분류 (HEADING, TABLE_ROW, LIST_ITEM, PARAGRAPH 등)
2. **블록 파서** — 연속 토큰을 블록으로 묶음 (HeadingNode, TableNode, ListNode 등)
3. **인라인 파서** — 블록 내부 문법 처리, **아래 우선순위 순서 엄수**
4. **렌더러** — AST → HTML 변환 (**이 단계에서만 XSS 이스케이프 적용**)

인라인 파서 우선순위 (높음 → 낮음):
```
{{{...}}}  >  '''굵기'''  >  ''기울임''  >  __밑줄__  >  ~~취소선~~
> `코드`  >  [[링크]]  >  [외부링크]  >  [* 각주]  >  $수식$  >  일반텍스트
```

파서가 반환하는 인터페이스 (변경 시 오케스트레이터 승인 필수):
```python
class RenderResult:
    html: str                # 렌더링된 HTML (XSS 이스케이프 완료)
    toc: list[TocEntry]      # 목차 [{level, text, anchor}]
    categories: list[str]    # 분류 목록
    links: list[str]         # 내부 링크 목록 (역링크 추적용)
    footnotes: list[str]     # 각주 목록
    redirect_to: str | None  # 넘겨주기 대상 (None이면 일반 문서)
```

### DB 테이블 그룹 (총 19개)

| 그룹 | 테이블 |
|------|--------|
| A. 위키 인스턴스 | `wikis` |
| B. 사용자 | `users`, `wiki_members`, `blocks` |
| C. 문서 (핵심) | `pages`, `page_revisions`, `revision_suppressions` |
| D. ACL 권한 | `page_acls`, `namespace_acls`, `user_acl_overrides` |
| E. 분류/파일 | `categories`, `page_categories`, `files` |
| F. 커뮤니티 | `discussions`, `discussion_comments`, `edit_requests` |
| G. 시스템 | `recent_changes`, `search_index`, `notifications` |

- `pages`: 현재 최신 상태 저장 (캐시 역할 포함)
- `page_revisions`: 전체 편집 이력 (소프트 삭제 적용)
- 스키마 변경 시 반드시 Alembic 마이그레이션 파일 생성

### 보안 규칙

> ⚠️ **모든 에이전트 필독 — 절대 위반 금지**

- ORM 사용 필수, **원시 SQL 직접 작성 금지**
- 파서 렌더러에서 **모든 사용자 입력 HTML 이스케이프** 적용
- `{{{#!html}}}` 원시 HTML 블록은 `admin` 권한 보유자만 사용 가능
- 외부 링크 `href`에서 `javascript:`, `vbscript:`, `data:` 프로토콜 제거
- Rate Limit: `slowapi` 라이브러리 사용
  - 로그인: 10회/분
  - 문서 편집: 60회/분
- 권한 검사는 **서버 사이드에서만** — 프론트 버튼 숨김은 UX일 뿐

---

## Phase 1 MVP 구현 우선순위

에이전트가 작업 순서를 판단할 때 이 순서를 참고한다:

```
1. [파서] 토크나이저 → 블록 파서 → 인라인 파서 → 렌더러 (기본 문법)
2. [백엔드] wikis / pages / page_revisions 모델 + CRUD API
3. [백엔드] ACL 권한 미들웨어 + 권한 검사 서비스
4. [백엔드] 인증 (회원가입 / 로그인 / JWT)
5. [프론트] 문서 보기 페이지 + 편집 페이지 (기본)
6. [QA] 파서 단위 테스트 + ACL 권한 매트릭스 통합 테스트
7. [백엔드] 검색 API (PostgreSQL FTS 먼저, Meilisearch 나중)
```