"""Page 서비스 — 문서 CRUD 및 revision 관리"""
from dataclasses import dataclass, field

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.page import Page
from app.models.page_revision import PageRevision
from app.parser import parse
from app.schemas.page import PageCreate, PageUpdate


@dataclass
class PageAuthor:
    """편집자 정보 — editor_id와 editor_ip를 묶어 전달"""

    id: int | None = None
    ip: str = field(default="0.0.0.0")


def _render_html(content: str) -> str:
    """나무마크 원본을 HTML로 렌더링 (파서 호출)"""
    result = parse(content)
    return result.html


def create_page(
    db: Session,
    wiki_id: int,
    data: PageCreate,
    author: PageAuthor | None = None,
) -> Page:
    """문서 생성 — 첫 번째 revision과 함께 생성"""
    if author is None:
        author = PageAuthor()

    # 문서 레코드 생성
    page = Page(
        wiki_id=wiki_id,
        namespace=data.namespace,
        slug=data.slug,
        title=data.title,
    )
    db.add(page)
    db.flush()  # page.id 확보

    # 첫 번째 revision 생성
    content_html = _render_html(data.content)
    byte_size = len(data.content.encode("utf-8"))
    revision = PageRevision(
        page_id=page.id,
        wiki_id=wiki_id,
        content=data.content,
        comment=data.comment,
        editor_id=author.id,
        editor_ip=author.ip,
        byte_size=byte_size,
        byte_diff=byte_size,
    )
    db.add(revision)
    db.flush()  # revision.id 확보

    # 문서 content 및 latest_revision 갱신
    page.content = data.content
    page.content_html = content_html
    page.latest_revision_id = revision.id
    db.commit()
    db.refresh(page)
    return page


def get_page(
    db: Session, wiki_id: int, namespace: str, slug: str
) -> Page | None:
    """wiki_id + namespace + slug로 활성 문서 조회"""
    stmt = select(Page).where(
        Page.wiki_id == wiki_id,
        Page.namespace == namespace,
        Page.slug == slug,
        Page.deleted_at.is_(None),
    )
    return db.scalar(stmt)


def update_page(
    db: Session,
    page: Page,
    data: PageUpdate,
    author: PageAuthor | None = None,
) -> Page:
    """문서 편집 — 새 revision을 생성하고 latest_revision_id 갱신"""
    if author is None:
        author = PageAuthor()

    # 이전 byte_size 계산 (byte_diff 산출용)
    prev_size = len((page.content or "").encode("utf-8"))
    new_size = len(data.content.encode("utf-8"))

    # 새 revision 생성
    content_html = _render_html(data.content)
    revision = PageRevision(
        page_id=page.id,
        wiki_id=page.wiki_id,
        content=data.content,
        comment=data.comment,
        editor_id=author.id,
        editor_ip=author.ip,
        byte_size=new_size,
        byte_diff=new_size - prev_size,
    )
    db.add(revision)
    db.flush()

    # 문서 메타 업데이트
    if data.title is not None:
        page.title = data.title
    page.content = data.content
    page.content_html = content_html
    page.latest_revision_id = revision.id

    db.commit()
    db.refresh(page)
    return page


def get_revision(
    db: Session, page_id: int, revision_id: int
) -> PageRevision | None:
    """특정 revision ID로 조회"""
    stmt = select(PageRevision).where(
        PageRevision.page_id == page_id,
        PageRevision.id == revision_id,
    )
    return db.scalar(stmt)


def list_revisions(
    db: Session, page_id: int, skip: int = 0, limit: int = 20
) -> tuple[list[PageRevision], int]:
    """편집 이력 목록 — (items, total) 반환, 최신 순"""
    base_filter = PageRevision.page_id == page_id

    count_stmt = select(func.count()).select_from(PageRevision).where(base_filter)
    total = db.scalar(count_stmt) or 0

    stmt = (
        select(PageRevision)
        .where(base_filter)
        .order_by(PageRevision.id.desc())
        .offset(skip)
        .limit(limit)
    )
    items = list(db.scalars(stmt).all())
    return items, total
