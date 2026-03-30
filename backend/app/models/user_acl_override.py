"""UserAclOverride 모델 — 사용자별 ACL 예외 설정"""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserAclOverride(Base):
    """사용자별 ACL 예외 설정 — 특정 위키에서 특정 사용자에게 등급 또는 액션 예외 부여"""

    __tablename__ = "user_acl_overrides"

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

    # 오버라이드 타입: grade_override / action_allow / action_deny
    override_type: Mapped[str] = mapped_column(String(20), nullable=False)

    # grade_override 사용 시 적용할 등급
    grade: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # action_allow / action_deny 사용 시 대상 액션
    action: Mapped[str | None] = mapped_column(String(20), nullable=True)

    reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # NULL = 무기한
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # 권한 부여자
    granted_by: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("users.id"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # 관계
    wiki: Mapped["Wiki"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Wiki", foreign_keys=[wiki_id]
    )
    user: Mapped["User"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "User", foreign_keys=[user_id]
    )
    granter: Mapped["User"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "User", foreign_keys=[granted_by]
    )
