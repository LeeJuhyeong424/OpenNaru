"""Wiki 서비스 — 위키 CRUD 비즈니스 로직"""
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.wiki import Wiki
from app.schemas.wiki import WikiCreate, WikiUpdate


def create_wiki(db: Session, data: WikiCreate) -> Wiki:
    """위키 생성"""
    wiki = Wiki(
        slug=data.slug,
        name=data.name,
        description=data.description,
        lang=data.lang,
        is_public=data.is_public,
        default_edit_acl=data.default_edit_acl,
        allow_anon_edit=data.allow_anon_edit,
    )
    db.add(wiki)
    db.commit()
    db.refresh(wiki)
    return wiki


def get_wiki_by_slug(db: Session, slug: str) -> Wiki | None:
    """slug로 활성 위키 조회 (소프트 삭제 제외)"""
    stmt = select(Wiki).where(Wiki.slug == slug, Wiki.deleted_at.is_(None))
    return db.scalar(stmt)


def list_wikis(db: Session, skip: int = 0, limit: int = 20) -> tuple[list[Wiki], int]:
    """위키 목록 조회 — (items, total) 반환"""
    base_filter = Wiki.deleted_at.is_(None)

    # 전체 개수
    count_stmt = select(func.count()).select_from(Wiki).where(base_filter)
    total = db.scalar(count_stmt) or 0

    # 목록
    stmt = (
        select(Wiki)
        .where(base_filter)
        .order_by(Wiki.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    items = list(db.scalars(stmt).all())
    return items, total


def update_wiki(db: Session, wiki: Wiki, data: WikiUpdate) -> Wiki:
    """위키 정보 수정 — None이 아닌 필드만 업데이트"""
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(wiki, field, value)
    db.commit()
    db.refresh(wiki)
    return wiki


def delete_wiki(db: Session, wiki: Wiki) -> None:
    """위키 소프트 삭제"""
    wiki.deleted_at = datetime.now(timezone.utc)
    db.commit()
