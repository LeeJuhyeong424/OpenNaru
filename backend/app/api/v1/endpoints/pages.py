"""문서 엔드포인트 — /wikis/{wiki_slug}/pages 관련 API"""
# revision 관련 라우트는 반드시 {page_slug:path} greedy 라우트 앞에 등록해야 함
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.page import Page
from app.models.wiki import Wiki
from app.schemas.common import PaginatedResponse
from app.schemas.page import (
    PageCreate,
    PageResponse,
    PageRevisionResponse,
    PageUpdate,
)
from app.services import page_service, wiki_service
from app.services.page_service import PageAuthor

router = APIRouter()


def _error(code: str, message: str, detail: str | None = None) -> dict:
    """표준 오류 응답 생성"""
    return {"code": code, "message": message, "detail": detail}


def _get_client_ip(request: Request) -> str:
    """클라이언트 IP 추출 (프록시 헤더 우선)"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "0.0.0.0"


def _get_wiki_or_404(db: Session, wiki_slug: str) -> Wiki:
    """위키 조회, 없으면 404"""
    wiki = wiki_service.get_wiki_by_slug(db, wiki_slug)
    if wiki is None:
        raise HTTPException(
            status_code=404,
            detail=_error("WIKI_NOT_FOUND", "위키를 찾을 수 없습니다."),
        )
    return wiki


def _get_page_or_404(db: Session, wiki_id: int, namespace: str, page_slug: str) -> Page:
    """문서 조회, 없으면 404"""
    page = page_service.get_page(db, wiki_id, namespace, page_slug)
    if page is None:
        raise HTTPException(
            status_code=404,
            detail=_error("PAGE_NOT_FOUND", "문서를 찾을 수 없습니다."),
        )
    return page


# --- 더 구체적인 경로를 먼저 등록 (path 컨버터 greedy 매칭 우회) ---

@router.get(
    "/{wiki_slug}/pages/{namespace}/{page_slug:path}/revisions/{rev_id}",
    response_model=PageRevisionResponse,
    summary="특정 revision 조회",
)
def get_revision(
    wiki_slug: str,
    namespace: str,
    page_slug: str,
    rev_id: int,
    db: Session = Depends(get_db),
) -> PageRevisionResponse:
    """특정 ID의 편집 이력을 조회합니다."""
    wiki = _get_wiki_or_404(db, wiki_slug)
    page = _get_page_or_404(db, wiki.id, namespace, page_slug)

    revision = page_service.get_revision(db, page.id, rev_id)
    if revision is None:
        raise HTTPException(
            status_code=404,
            detail=_error("REVISION_NOT_FOUND", f"revision {rev_id}을 찾을 수 없습니다."),
        )
    return PageRevisionResponse.from_orm_model(revision)


@router.get(
    "/{wiki_slug}/pages/{namespace}/{page_slug:path}/revisions",
    response_model=PaginatedResponse[PageRevisionResponse],
    summary="편집 이력 목록",
)
def list_revisions(
    wiki_slug: str,
    namespace: str,
    page_slug: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> PaginatedResponse[PageRevisionResponse]:
    """문서의 편집 이력을 최신 순으로 반환합니다."""
    wiki = _get_wiki_or_404(db, wiki_slug)
    page = _get_page_or_404(db, wiki.id, namespace, page_slug)

    items, total = page_service.list_revisions(db, page.id, skip=skip, limit=limit)
    return PaginatedResponse(
        items=[PageRevisionResponse.from_orm_model(r) for r in items],
        total=total,
        skip=skip,
        limit=limit,
    )


# --- 일반 문서 CRUD (path 컨버터 라우트는 더 구체적인 경로 뒤에 등록) ---

@router.get(
    "/{wiki_slug}/pages/{namespace}/{page_slug:path}",
    response_model=PageResponse,
    summary="문서 조회",
)
def get_page(
    wiki_slug: str,
    namespace: str,
    page_slug: str,
    db: Session = Depends(get_db),
) -> PageResponse:
    """문서를 조회합니다. 없는 경우 404와 함께 생성 가능 여부를 반환합니다."""
    wiki = _get_wiki_or_404(db, wiki_slug)

    page = page_service.get_page(db, wiki.id, namespace, page_slug)
    if page is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "PAGE_NOT_FOUND",
                "message": "문서를 찾을 수 없습니다.",
                "exists": False,
                "can_create": True,
            },
        )
    return PageResponse.from_orm_model(page, wiki_slug)


@router.post(
    "/{wiki_slug}/pages",
    response_model=PageResponse,
    status_code=201,
    summary="문서 생성",
)
def create_page(
    wiki_slug: str,
    data: PageCreate,
    request: Request,
    db: Session = Depends(get_db),
) -> PageResponse:
    """새 문서를 생성합니다."""
    wiki = _get_wiki_or_404(db, wiki_slug)

    # 중복 문서 확인
    if page_service.get_page(db, wiki.id, data.namespace, data.slug) is not None:
        raise HTTPException(
            status_code=409,
            detail=_error(
                "PAGE_ALREADY_EXISTS",
                f"'{data.namespace}:{data.slug}' 문서가 이미 존재합니다.",
            ),
        )

    # 인증 미구현 단계 — author_id는 None
    author = PageAuthor(id=None, ip=_get_client_ip(request))
    page = page_service.create_page(db, wiki.id, data, author)
    return PageResponse.from_orm_model(page, wiki_slug)


@router.patch(
    "/{wiki_slug}/pages/{namespace}/{page_slug:path}",
    response_model=PageResponse,
    summary="문서 편집",
)
def update_page(
    wiki_slug: str,
    namespace: str,
    page_slug: str,
    data: PageUpdate,
    request: Request,
    db: Session = Depends(get_db),
) -> PageResponse:
    """문서를 편집합니다. 새 revision이 생성됩니다."""
    wiki = _get_wiki_or_404(db, wiki_slug)
    page = _get_page_or_404(db, wiki.id, namespace, page_slug)

    author = PageAuthor(id=None, ip=_get_client_ip(request))
    updated = page_service.update_page(db, page, data, author)
    return PageResponse.from_orm_model(updated, wiki_slug)
