"""Discussion 모델 — 문서 토론"""
from sqlalchemy import BigInteger, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import SoftDeleteMixin, TimestampMixin


class Discussion(TimestampMixin, SoftDeleteMixin, Base):
    """문서 토론 — 특정 문서에 대한 토론 스레드"""

    __tablename__ = "discussions"

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

    # 토론 개설자 (NULL = 비로그인)
    author_id: Mapped[int | None] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("users.id"),
        nullable=True,
    )

    title: Mapped[str] = mapped_column(String(300), nullable=False)

    # 토론 상태: open / closed
    status: Mapped[str] = mapped_column(String(20), default="open", nullable=False)

    # 댓글 수 (캐시값)
    comment_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 관계
    wiki: Mapped["Wiki"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Wiki", foreign_keys=[wiki_id]
    )
    page: Mapped["Page"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Page", foreign_keys=[page_id]
    )
    author: Mapped["User | None"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "User", foreign_keys=[author_id]
    )
    comments: Mapped[list["DiscussionComment"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "DiscussionComment", back_populates="discussion", cascade="all, delete-orphan"
    )
