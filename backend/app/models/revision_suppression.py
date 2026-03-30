"""RevisionSuppression 모델 — 편집 이력 말소 기록"""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class RevisionSuppression(Base):
    """편집 이력 말소 기록 — 어떤 관리자가 어떤 이유로 이력을 말소했는지 추적"""

    __tablename__ = "revision_suppressions"

    # 내부용 기본키 (SQLite 호환: Integer로 fallback)
    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )

    revision_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("page_revisions.id"),
        nullable=False,
        index=True,
    )

    # 말소 처리한 관리자
    suppressed_by: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("users.id"),
        nullable=False,
    )

    reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # 관계
    revision: Mapped["PageRevision"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "PageRevision", foreign_keys=[revision_id]
    )
    suppressor: Mapped["User"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "User", foreign_keys=[suppressed_by]
    )
