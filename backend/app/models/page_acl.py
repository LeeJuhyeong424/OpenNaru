"""PageAcl 모델 — 문서 단위 ACL"""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PageAcl(Base):
    """문서 단위 ACL — 특정 문서에 대한 액션별 접근 등급 설정"""

    __tablename__ = "page_acls"
    __table_args__ = (
        # 한 문서에 동일 action은 하나의 ACL만 허용
        UniqueConstraint("page_id", "action", name="uq_page_acls_page_action"),
    )

    # 내부용 기본키 (SQLite 호환: Integer로 fallback)
    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )

    page_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("pages.id"),
        nullable=False,
        index=True,
    )

    # 액션: read / edit / discuss / move / delete
    action: Mapped[str] = mapped_column(String(20), nullable=False)

    # 허용 최소 등급: blocked/anonymous/member/autoconf/admin/sysadmin
    acl_value: Mapped[str] = mapped_column(String(20), nullable=False)

    # ACL 설정자 (NULL = 시스템 기본)
    created_by: Mapped[int | None] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("users.id"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # 관계
    page: Mapped["Page"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Page", foreign_keys=[page_id]
    )
    creator: Mapped["User | None"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "User", foreign_keys=[created_by]
    )
