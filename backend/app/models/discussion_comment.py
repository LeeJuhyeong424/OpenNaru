"""DiscussionComment 모델 — 토론 댓글"""
from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import SoftDeleteMixin, TimestampMixin


class DiscussionComment(TimestampMixin, SoftDeleteMixin, Base):
    """토론 댓글"""

    __tablename__ = "discussion_comments"

    # 내부용 기본키 (SQLite 호환: Integer로 fallback)
    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )

    discussion_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("discussions.id"),
        nullable=False,
        index=True,
    )

    # 작성자 (NULL = 비로그인)
    author_id: Mapped[int | None] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("users.id"),
        nullable=True,
    )

    content: Mapped[str] = mapped_column(Text, default="", nullable=False)

    # 관리자에 의한 숨김 처리
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # 관계
    discussion: Mapped["Discussion"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Discussion", back_populates="comments"
    )
    author: Mapped["User | None"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "User", foreign_keys=[author_id]
    )
