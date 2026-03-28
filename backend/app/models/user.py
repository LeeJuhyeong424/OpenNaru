"""User 모델 — 위키 사용자 계정"""
import uuid as uuid_module

from sqlalchemy import BigInteger, Boolean, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class User(TimestampMixin, Base):
    """사용자 계정 모델 (소프트 삭제 없음, is_active로 비활성화)"""

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

    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(100), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    edit_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 관계 — 역참조
    owned_wikis: Mapped[list["Wiki"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Wiki", back_populates="owner", foreign_keys="Wiki.owner_id"
    )
    wiki_memberships: Mapped[list["WikiMember"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "WikiMember", back_populates="user"
    )
    page_revisions: Mapped[list["PageRevision"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "PageRevision", back_populates="author"
    )
