"""Block 모델 — IP/사용자 차단 기록"""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class Block(TimestampMixin, Base):
    """IP 또는 사용자 차단 기록

    wiki_id가 NULL이면 전역 차단, 값이 있으면 해당 위키 내 차단.
    """

    __tablename__ = "blocks"

    # 내부용 기본키 (SQLite 호환: Integer로 fallback)
    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )

    # NULL = 전역 차단
    wiki_id: Mapped[int | None] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("wikis.id"),
        nullable=True,
        index=True,
    )

    # 차단 대상 — IP 또는 사용자 (둘 중 하나만 존재)
    # INET은 PostgreSQL 전용이므로 String(45) 사용 (IPv6 포함 최대 45자)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_id: Mapped[int | None] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 차단 집행자
    blocked_by: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("users.id"),
        nullable=False,
    )

    # NULL = 영구 차단
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # 관계
    wiki: Mapped["Wiki | None"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Wiki", foreign_keys=[wiki_id]
    )
    user: Mapped["User | None"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "User", foreign_keys=[user_id]
    )
    blocker: Mapped["User"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "User", foreign_keys=[blocked_by]
    )
