"""Page / PageRevision Pydantic 스키마 — 요청/응답 모델"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PageCreate(BaseModel):
    """문서 생성 요청"""

    namespace: str = Field("main", max_length=30)
    slug: str = Field(..., min_length=1, max_length=500)
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., description="나무마크 원본 내용")
    comment: str = Field("", max_length=500, description="편집 요약")


class PageUpdate(BaseModel):
    """문서 편집 요청 — 새 revision을 생성함"""

    content: str = Field(..., description="나무마크 원본 내용")
    comment: str = Field("", max_length=500, description="편집 요약")
    title: str | None = Field(None, min_length=1, max_length=500)


class PageRevisionResponse(BaseModel):
    """편집 이력 단건 응답"""

    model_config = ConfigDict(from_attributes=True)

    id: int  # revision ID (BIGSERIAL — 버전 식별에 사용)
    editor_username: str | None  # 비로그인이면 None
    editor_ip: str | None
    content: str
    comment: str | None
    is_minor: bool
    is_bot: bool
    byte_size: int
    byte_diff: int
    is_suppressed: bool
    created_at: datetime

    @classmethod
    def from_orm_model(cls, rev: object) -> "PageRevisionResponse":
        editor_username = None
        if rev.editor is not None:  # type: ignore[attr-defined]
            editor_username = rev.editor.username  # type: ignore[attr-defined]
        return cls(
            id=rev.id,  # type: ignore[attr-defined]
            editor_username=editor_username,
            editor_ip=str(rev.editor_ip) if rev.editor_ip else None,  # type: ignore[attr-defined]
            content=rev.content,  # type: ignore[attr-defined]
            comment=rev.comment,  # type: ignore[attr-defined]
            is_minor=rev.is_minor,  # type: ignore[attr-defined]
            is_bot=rev.is_bot,  # type: ignore[attr-defined]
            byte_size=rev.byte_size,  # type: ignore[attr-defined]
            byte_diff=rev.byte_diff,  # type: ignore[attr-defined]
            is_suppressed=rev.is_suppressed,  # type: ignore[attr-defined]
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
    content_html: str  # 렌더링된 HTML (html_cache → content_html)
    ai_summary: str | None
    latest_revision_id: int | None
    is_redirect: bool
    redirect_to: str | None
    protection_level: str
    view_count: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm_model(cls, page: object, wiki_slug: str) -> "PageResponse":
        return cls(
            id=page.uuid,  # type: ignore[attr-defined]
            wiki_slug=wiki_slug,
            namespace=page.namespace,  # type: ignore[attr-defined]
            slug=page.slug,  # type: ignore[attr-defined]
            title=page.title,  # type: ignore[attr-defined]
            content_html=page.content_html,  # type: ignore[attr-defined]
            ai_summary=page.ai_summary,  # type: ignore[attr-defined]
            latest_revision_id=page.latest_revision_id,  # type: ignore[attr-defined]
            is_redirect=page.is_redirect,  # type: ignore[attr-defined]
            redirect_to=page.redirect_to,  # type: ignore[attr-defined]
            protection_level=page.protection_level,  # type: ignore[attr-defined]
            view_count=page.view_count,  # type: ignore[attr-defined]
            created_at=page.created_at,  # type: ignore[attr-defined]
            updated_at=page.updated_at,  # type: ignore[attr-defined]
        )
