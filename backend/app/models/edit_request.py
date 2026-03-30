"""EditRequest 모델 — 편집 요청 (보호 문서 편집 제안)"""
from sqlalchemy import BigInteger, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class EditRequest(TimestampMixin, Base):
    """편집 요청 — 편집이 제한된 문서에 대한 변경 제안"""

    __tablename__ = "edit_requests"

    # 내부용 기본키 (SQLite 호환: Integer로 fallback)
    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )

    wiki_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("wikis.id"),
        nullable=False,
        index=True,
    )
    page_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("pages.id"),
        nullable=False,
        index=True,
    )

    # 요청자 (NULL = 비로그인)
    requester_id: Mapped[int | None] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("users.id"),
        nullable=True,
    )
    # INET은 PostgreSQL 전용이므로 String(45) 사용
    requester_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)

    # 현재 본문과 제안 본문
    original_content: Mapped[str] = mapped_column(Text, default="", nullable=False)
    proposed_content: Mapped[str] = mapped_column(Text, default="", nullable=False)

    # 변경 사유
    comment: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # 처리 상태: pending / approved / rejected
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)

    # 검토자 (NULL = 미처리)
    reviewed_by: Mapped[int | None] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("users.id"),
        nullable=True,
    )
    reject_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 관계
    wiki: Mapped["Wiki"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Wiki", foreign_keys=[wiki_id]
    )
    page: Mapped["Page"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Page", foreign_keys=[page_id]
    )
    requester: Mapped["User | None"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "User", foreign_keys=[requester_id]
    )
    reviewer: Mapped["User | None"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "User", foreign_keys=[reviewed_by]
    )
