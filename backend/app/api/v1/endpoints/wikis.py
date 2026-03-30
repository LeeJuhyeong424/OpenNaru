"""위키 엔드포인트 — /wikis 관련 CRUD API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.wiki import WikiCreate, WikiListResponse, WikiResponse, WikiUpdate
from app.services import wiki_service

router = APIRouter()


def _error(code: str, message: str, detail: str | None = None) -> dict:
    """표준 오류 응답 생성"""
    return {"code": code, "message": message, "detail": detail}


@router.get("", response_model=WikiListResponse, summary="위키 목록 조회")
def list_wikis(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> WikiListResponse:
    """공개 위키 목록을 반환합니다."""
    items, total = wiki_service.list_wikis(db, skip=skip, limit=limit)
    return WikiListResponse(
        items=[WikiResponse.from_orm_model(w) for w in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post("", response_model=WikiResponse, status_code=201, summary="위키 생성")
def create_wiki(
    data: WikiCreate,
    db: Session = Depends(get_db),
) -> WikiResponse:
    """새 위키를 생성합니다."""
    # slug 중복 확인
    existing = wiki_service.get_wiki_by_slug(db, data.slug)
    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail=_error("WIKI_SLUG_CONFLICT", f"슬러그 '{data.slug}'는 이미 사용 중입니다."),
        )
    # 인증 미구현 단계
    wiki = wiki_service.create_wiki(db, data)
    return WikiResponse.from_orm_model(wiki)


@router.get("/{wiki_slug}", response_model=WikiResponse, summary="위키 조회")
def get_wiki(
    wiki_slug: str,
    db: Session = Depends(get_db),
) -> WikiResponse:
    """slug로 위키를 조회합니다."""
    wiki = wiki_service.get_wiki_by_slug(db, wiki_slug)
    if wiki is None:
        raise HTTPException(
            status_code=404,
            detail=_error("WIKI_NOT_FOUND", "위키를 찾을 수 없습니다."),
        )
    return WikiResponse.from_orm_model(wiki)


@router.patch("/{wiki_slug}", response_model=WikiResponse, summary="위키 수정")
def update_wiki(
    wiki_slug: str,
    data: WikiUpdate,
    db: Session = Depends(get_db),
) -> WikiResponse:
    """위키 정보를 수정합니다."""
    wiki = wiki_service.get_wiki_by_slug(db, wiki_slug)
    if wiki is None:
        raise HTTPException(
            status_code=404,
            detail=_error("WIKI_NOT_FOUND", "위키를 찾을 수 없습니다."),
        )
    updated = wiki_service.update_wiki(db, wiki, data)
    return WikiResponse.from_orm_model(updated)


@router.delete("/{wiki_slug}", status_code=204, summary="위키 삭제")
def delete_wiki(
    wiki_slug: str,
    db: Session = Depends(get_db),
) -> None:
    """위키를 소프트 삭제합니다."""
    wiki = wiki_service.get_wiki_by_slug(db, wiki_slug)
    if wiki is None:
        raise HTTPException(
            status_code=404,
            detail=_error("WIKI_NOT_FOUND", "위키를 찾을 수 없습니다."),
        )
    wiki_service.delete_wiki(db, wiki)
