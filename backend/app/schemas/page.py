"""Page / PageRevision Pydantic 스키마 — 요청/응답 모델"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PageCreate(BaseModel):
    """문서 생성 요청"""

    namespace: str = Field("main", max_length=50)
    slug: str = Field(..., min_length=1, max_length=500)
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., description="나무마크 원본 내용")
    summary: str = Field("", max_length=500, description="편집 요약")


class PageUpdate(BaseModel):
    """문서 편집 요청 — 새 revision을 생성함"""

    content: str = Field(..., description="나무마크 원본 내용")
    summary: str = Field("", max_length=500, description="편집 요약")
    title: str | None = Field(None, min_length=1, max_length=500)


class PageRevisionResponse(BaseModel):
    """편집 이력 단건 응답"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID  # revision UUID
    revision_number: int
    content: str
    summary: str
    author_username: str | None  # 비로그인이면 None
    author_ip: str | None
    is_hidden: bool
    created_at: datetime

    @classmethod
    def from_orm_model(cls, rev: object) -> "PageRevisionResponse":
        author_username = None
        if rev.author is not None:  # type: ignore[attr-defined]
            author_username = rev.author.username  # type: ignore[attr-defined]
        return cls(
            id=rev.uuid,  # type: ignore[attr-defined]
            revision_number=rev.revision_number,  # type: ignore[attr-defined]
            content=rev.content,  # type: ignore[attr-defined]
            summary=rev.summary,  # type: ignore[attr-defined]
            author_username=author_username,
            author_ip=str(rev.author_ip) if rev.author_ip else None,  # type: ignore[attr-defined]
            is_hidden=rev.is_hidden,  # type: ignore[attr-defined]
            created_at=rev.created_at,  # type: ignore[attr-defined]
        )


class PageResponse(BaseModel):
    """문서 응답"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID  # page UUID
    wiki_slug: str
    namespace: str
    slug: str
    title: str
    html_cache: str | None
    current_revision_number: int | None
    is_redirect: bool
    redirect_to: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm_model(cls, page: object, wiki_slug: str) -> "PageResponse":
        current_revision_number = None
        html_cache = None
        if page.current_revision is not None:  # type: ignore[attr-defined]
            current_revision_number = page.current_revision.revision_number  # type: ignore[attr-defined]
            html_cache = page.current_revision.html_cache  # type: ignore[attr-defined]
        return cls(
            id=page.uuid,  # type: ignore[attr-defined]
            wiki_slug=wiki_slug,
            namespace=page.namespace,  # type: ignore[attr-defined]
            slug=page.slug,  # type: ignore[attr-defined]
            title=page.title,  # type: ignore[attr-defined]
            html_cache=html_cache,
            current_revision_number=current_revision_number,
            is_redirect=page.is_redirect,  # type: ignore[attr-defined]
            redirect_to=page.redirect_to,  # type: ignore[attr-defined]
            created_at=page.created_at,  # type: ignore[attr-defined]
            updated_at=page.updated_at,  # type: ignore[attr-defined]
        )
