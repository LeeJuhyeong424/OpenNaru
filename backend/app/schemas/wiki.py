"""Wiki Pydantic 스키마 — 요청/응답 모델"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class WikiCreate(BaseModel):
    """위키 생성 요청"""

    slug: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z0-9-]+$")
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    is_public: bool = True
    default_read_level: str = Field("anonymous", max_length=20)
    default_edit_level: str = Field("anonymous", max_length=20)


class WikiUpdate(BaseModel):
    """위키 수정 요청 — 모든 필드 선택적"""

    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    is_public: bool | None = None
    default_read_level: str | None = Field(None, max_length=20)
    default_edit_level: str | None = Field(None, max_length=20)


class WikiResponse(BaseModel):
    """위키 응답 — 내부 id 노출 금지, uuid 사용"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID  # 내부 BIGSERIAL이 아닌 UUID 노출
    slug: str
    name: str
    description: str | None
    is_public: bool
    default_read_level: str
    default_edit_level: str
    created_at: datetime
    updated_at: datetime

    # ORM에서 uuid 컬럼을 id로 매핑하기 위한 validator
    @classmethod
    def from_orm_model(cls, wiki: object) -> "WikiResponse":
        return cls(
            id=wiki.uuid,  # type: ignore[attr-defined]
            slug=wiki.slug,  # type: ignore[attr-defined]
            name=wiki.name,  # type: ignore[attr-defined]
            description=wiki.description,  # type: ignore[attr-defined]
            is_public=wiki.is_public,  # type: ignore[attr-defined]
            default_read_level=wiki.default_read_level,  # type: ignore[attr-defined]
            default_edit_level=wiki.default_edit_level,  # type: ignore[attr-defined]
            created_at=wiki.created_at,  # type: ignore[attr-defined]
            updated_at=wiki.updated_at,  # type: ignore[attr-defined]
        )


class WikiListResponse(BaseModel):
    """위키 목록 응답"""

    items: list[WikiResponse]
    total: int
    skip: int
    limit: int
