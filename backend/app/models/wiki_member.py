"""WikiMember 모델 — 위키-사용자 관계 및 역할"""
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class WikiMember(Base):
    """위키 멤버 모델 — 위키별 사용자 역할 및 차단 관리"""

    __tablename__ = "wiki_members"
    __table_args__ = (
        # 한 위키에 동일 사용자는 하나의 레코드만 허용
        UniqueConstraint("wiki_id", "user_id", name="uq_wiki_members_wiki_user"),
    )

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
    user_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    # 역할: member / editor / admin
    role: Mapped[str] = mapped_column(String(20), default="member", nullable=False)

    # 차단 정보
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    blocked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    block_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    # NULL = 영구 차단
    block_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # 가입/수정 시각
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="now()",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="now()",
        onupdate="now()",
    )

    # 관계
    wiki: Mapped["Wiki"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Wiki", back_populates="members"
    )
    user: Mapped["User"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "User", back_populates="wiki_memberships"
    )
