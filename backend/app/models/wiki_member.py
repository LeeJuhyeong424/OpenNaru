"""WikiMember 모델 — 위키-사용자 관계 및 역할"""
from sqlalchemy import BigInteger, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class WikiMember(TimestampMixin, Base):
    """위키 멤버 모델 — 위키별 사용자 역할 관리"""

    __tablename__ = "wiki_members"
    __table_args__ = (
        # 한 위키에 동일 사용자는 하나의 역할만 가짐
        UniqueConstraint("wiki_id", "user_id", name="uq_wiki_members_wiki_user"),
    )

    # 내부용 기본키 (SQLite 호환: Integer로 fallback)
    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )

    wiki_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("wikis.id"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=False, index=True
    )

    # 역할: admin / member / blocked
    role: Mapped[str] = mapped_column(String(20), nullable=False)

    # 관계
    wiki: Mapped["Wiki"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Wiki", back_populates="members"
    )
    user: Mapped["User"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "User", back_populates="wiki_memberships"
    )
