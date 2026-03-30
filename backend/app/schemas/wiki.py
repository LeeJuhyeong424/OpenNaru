"""Wiki Pydantic 스키마 — 요청/응답 모델"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class WikiCreate(BaseModel):
    """위키 생성 요청"""

    slug: str = Field(..., min_length=1, max_length=60, pattern=r"^[a-z0-9-]+$")
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=2000)
    lang: str = Field("ko", max_length=10)
    is_public: bool = True
    default_edit_acl: str = Field("anonymous", max_length=20)
    allow_anon_edit: bool = False


class WikiUpdate(BaseModel):
    """위키 수정 요청 — 모든 필드 선택적"""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=2000)
    lang: str | None = Field(None, max_length=10)
    is_public: bool | None = None
    default_edit_acl: str | None = Field(None, max_length=20)
    allow_anon_edit: bool | None = None


class WikiResponse(BaseModel):
    """위키 응답 — 내부 id 노출 금지, uuid 사용"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID  # 내부 BIGSERIAL이 아닌 UUID 노출
    slug: str
    name: str
    description: str | None
    lang: str
    is_public: bool
    default_edit_acl: str
    allow_anon_edit: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm_model(cls, wiki: object) -> "WikiResponse":
        return cls(
            id=wiki.uuid,  # type: ignore[attr-defined]
            slug=wiki.slug,  # type: ignore[attr-defined]
            name=wiki.name,  # type: ignore[attr-defined]
            description=wiki.description,  # type: ignore[attr-defined]
            lang=wiki.lang,  # type: ignore[attr-defined]
            is_public=wiki.is_public,  # type: ignore[attr-defined]
            default_edit_acl=wiki.default_edit_acl,  # type: ignore[attr-defined]
            allow_anon_edit=wiki.allow_anon_edit,  # type: ignore[attr-defined]
            created_at=wiki.created_at,  # type: ignore[attr-defined]
            updated_at=wiki.updated_at,  # type: ignore[attr-defined]
        )


class WikiListResponse(BaseModel):
    """위키 목록 응답"""

    items: list[WikiResponse]
    total: int
    skip: int
    limit: int
