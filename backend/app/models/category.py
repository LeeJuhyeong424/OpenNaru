"""Category 모델 — 위키 카테고리 (트리 구조)"""
from sqlalchemy import BigInteger, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class Category(TimestampMixin, Base):
    """위키 카테고리 — 계층 구조(자기 참조) 지원"""

    __tablename__ = "categories"
    __table_args__ = (
        # 같은 위키 내에서 slug는 유일
        UniqueConstraint("wiki_id", "slug", name="uq_categories_wiki_slug"),
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

    slug: Mapped[str] = mapped_column(String(300), nullable=False)
    name: Mapped[str] = mapped_column(String(300), nullable=False)

    # 부모 카테고리 (NULL = 최상위)
    parent_id: Mapped[int | None] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("categories.id"),
        nullable=True,
    )

    # 소속 문서 수 (캐시값)
    page_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 관계
    wiki: Mapped["Wiki"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Wiki", foreign_keys=[wiki_id]
    )
    # 자기 참조 — 부모 카테고리
    parent: Mapped["Category | None"] = relationship(
        "Category",
        remote_side="Category.id",
        foreign_keys=[parent_id],
        back_populates="children",
    )
    # 자기 참조 — 자식 카테고리 목록
    children: Mapped[list["Category"]] = relationship(
        "Category",
        foreign_keys=[parent_id],
        back_populates="parent",
    )
