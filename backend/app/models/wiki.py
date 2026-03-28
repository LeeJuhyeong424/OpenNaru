"""Wiki 모델 — 위키 공간 단위"""
import uuid as uuid_module

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import SoftDeleteMixin, TimestampMixin


class Wiki(TimestampMixin, SoftDeleteMixin, Base):
    """위키 모델 — 독립된 위키 공간"""

    __tablename__ = "wikis"

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

    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # ACL 기본값 — blocked/anonymous/member/autoconf/admin/sysadmin
    default_read_level: Mapped[str] = mapped_column(
        String(20), default="anonymous", nullable=False
    )
    default_edit_level: Mapped[str] = mapped_column(
        String(20), default="anonymous", nullable=False
    )

    # 소유자 FK (삭제된 위키도 이력 보존을 위해 NULL 허용)
    owner_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=True
    )

    # 관계
    owner: Mapped["User | None"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "User", back_populates="owned_wikis", foreign_keys=[owner_id]
    )
    members: Mapped[list["WikiMember"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "WikiMember", back_populates="wiki", cascade="all, delete-orphan"
    )
    pages: Mapped[list["Page"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Page", back_populates="wiki", cascade="all, delete-orphan"
    )
