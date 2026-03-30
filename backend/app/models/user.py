"""User 모델 — 위키 사용자 계정"""
import uuid as uuid_module
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import SoftDeleteMixin, TimestampMixin


class User(TimestampMixin, SoftDeleteMixin, Base):
    """사용자 계정 모델"""

    __tablename__ = "users"

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

    username: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # 소셜 로그인 시 NULL 허용
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # 소셜 로그인 정보
    oauth_provider: Mapped[str | None] = mapped_column(String(30), nullable=True)
    oauth_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # 아바타 파일 FK — 순환참조 방지를 위해 직접 FK 제약 없이 BigInteger 사용
    avatar_file_id: Mapped[int | None] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"), nullable=True
    )

    # 전역 관리자 여부
    is_global_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # 계정 차단 여부
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # 마지막 로그인 시각
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # 관계 — 역참조
    wiki_memberships: Mapped[list["WikiMember"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "WikiMember", back_populates="user"
    )
    page_revisions: Mapped[list["PageRevision"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "PageRevision", back_populates="editor", foreign_keys="PageRevision.editor_id"
    )
