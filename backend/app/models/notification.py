"""Notification 모델 — 사용자 알림"""
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Notification(Base):
    """사용자 알림 — 편집 승인, 토론 댓글 등 다양한 이벤트 알림"""

    __tablename__ = "notifications"

    # 내부용 기본키 (SQLite 호환: Integer로 fallback)
    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )

    # 알림 수신자
    user_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    # 관련 위키 (NULL = 전역 알림)
    wiki_id: Mapped[int | None] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("wikis.id"),
        nullable=True,
    )

    # 알림 타입: edit_approved / discussion_reply / mention 등
    type: Mapped[str] = mapped_column(String(40), nullable=False)

    # 참조 ID (알림 타입에 따라 revision_id, discussion_id 등)
    ref_id: Mapped[int | None] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"), nullable=True
    )

    message: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # 관계
    user: Mapped["User"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "User", foreign_keys=[user_id]
    )
    wiki: Mapped["Wiki | None"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Wiki", foreign_keys=[wiki_id]
    )
