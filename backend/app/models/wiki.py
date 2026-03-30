"""Wiki 모델 — 위키 공간 단위"""
import uuid as uuid_module

from sqlalchemy import JSON, BigInteger, Boolean, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import SoftDeleteMixin, TimestampMixin


class Wiki(TimestampMixin, SoftDeleteMixin, Base):
    """위키 모델 — 독립된 위키 공간"""

    __tablename__ = "wikis"

    # 내부용 기본키 (SQLite 호환: Integer로 fallback)
    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    # 외부 노출용 UUID
    uuid: Mapped[uuid_module.UUID] = mapped_column(
        Uuid(as_uuid=True),
        default=uuid_module.uuid4,
        unique=True,
        nullable=False,
        index=True,
    )

    slug: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 로고 파일 FK — 순환참조 방지를 위해 직접 FK 제약 없이 BigInteger 사용
    logo_file_id: Mapped[int | None] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"), nullable=True
    )

    # 언어 설정 (ko, en 등)
    lang: Mapped[str] = mapped_column(String(10), default="ko", nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # 위키 기본 편집 등급 — blocked/anonymous/member/autoconf/admin/sysadmin
    default_edit_acl: Mapped[str] = mapped_column(
        String(20), default="anonymous", nullable=False
    )
    # 익명 편집 허용 여부
    allow_anon_edit: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # 위키 설정 (JSONB/JSON/TEXT 멀티DB 호환)
    settings: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    # 관계
    members: Mapped[list["WikiMember"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "WikiMember", back_populates="wiki", cascade="all, delete-orphan"
    )
    pages: Mapped[list["Page"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Page", back_populates="wiki", cascade="all, delete-orphan"
    )
