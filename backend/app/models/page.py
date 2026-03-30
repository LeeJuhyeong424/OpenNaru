"""Page 모델 — 위키 문서"""
import uuid as uuid_module

from sqlalchemy import (
    BigInteger,
    Boolean,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import SoftDeleteMixin, TimestampMixin


class Page(TimestampMixin, SoftDeleteMixin, Base):
    """위키 문서 모델"""

    __tablename__ = "pages"
    __table_args__ = (
        # 같은 위키, 같은 네임스페이스에서 slug는 유일해야 함
        UniqueConstraint("wiki_id", "namespace", "slug", name="uq_pages_wiki_ns_slug"),
    )

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

    wiki_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("wikis.id"),
        nullable=False,
        index=True,
    )

    # 네임스페이스: main / talk / user / file / template / help
    namespace: Mapped[str] = mapped_column(
        String(30), default="main", nullable=False
    )
    slug: Mapped[str] = mapped_column(String(500), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)

    # 나무마크 원문 (pages에도 저장 — 캐시 역할)
    content: Mapped[str] = mapped_column(Text, default="", nullable=False)
    # 렌더링된 HTML 캐시
    content_html: Mapped[str] = mapped_column(Text, default="", nullable=False)
    # AI 요약
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 최신 revision FK (use_alter=True 로 순환참조 방지)
    latest_revision_id: Mapped[int | None] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("page_revisions.id", use_alter=True, name="fk_pages_latest_revision"),
        nullable=True,
    )

    # 리다이렉트 정보
    redirect_to: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_redirect: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # 보호 등급: none / member / autoconf / admin
    protection_level: Mapped[str] = mapped_column(
        String(20), default="none", nullable=False
    )

    # 조회수
    view_count: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"), default=0, nullable=False
    )

    # 관계
    wiki: Mapped["Wiki"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Wiki", back_populates="pages"
    )
    latest_revision: Mapped["PageRevision | None"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "PageRevision",
        foreign_keys=[latest_revision_id],
        post_update=True,
    )
    revisions: Mapped[list["PageRevision"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "PageRevision",
        back_populates="page",
        foreign_keys="PageRevision.page_id",
        cascade="all, delete-orphan",
        order_by="PageRevision.id",
    )
