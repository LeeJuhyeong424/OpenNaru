"""PageRevision 모델 — 문서 편집 이력 (불변 레코드)"""
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
from app.models.base import TimestampMixin


class PageRevision(TimestampMixin, Base):
    """문서 편집 이력 — 한 번 생성되면 수정 불가 (불변 레코드)"""

    __tablename__ = "page_revisions"
    __table_args__ = (
        # 같은 문서에서 revision_number는 유일해야 함
        UniqueConstraint("page_id", "revision_number", name="uq_page_revisions_page_rev"),
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

    page_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("pages.id"), nullable=False, index=True
    )
    revision_number: Mapped[int] = mapped_column(Integer, nullable=False)

    # 나무마크 원문
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # 렌더링된 HTML 캐시 (NULL이면 요청 시 생성)
    html_cache: Mapped[str | None] = mapped_column(Text, nullable=True)
    # 편집 요약
    summary: Mapped[str] = mapped_column(String(500), default="", nullable=False)

    # 편집자 정보 — 로그인: author_id, 비로그인: author_ip
    author_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=True
    )
    # INET은 PostgreSQL 전용이므로 String(45)로 대체 (SQLite/MySQL 호환)
    author_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)

    # 이력 말소 플래그 (관리자 처리)
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # updated_at은 불변 레코드이므로 사용하지 않지만 TimestampMixin에 포함됨

    # 관계
    page: Mapped["Page"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Page",
        back_populates="revisions",
        foreign_keys=[page_id],
    )
    author: Mapped["User | None"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "User", back_populates="page_revisions"
    )
