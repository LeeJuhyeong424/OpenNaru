"""PageCategory 모델 — 문서-카테고리 다대다 관계"""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PageCategory(Base):
    """문서-카테고리 연결 테이블"""

    __tablename__ = "page_categories"
    __table_args__ = (
        # 같은 문서-카테고리 쌍은 한 번만 허용
        UniqueConstraint("page_id", "category_id", name="uq_page_categories_page_cat"),
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
    category_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("categories.id"),
        nullable=False,
        index=True,
    )

    # 정렬 키 (사전순 정렬 시 사용)
    sort_key: Mapped[str | None] = mapped_column(String(300), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # 관계
    page: Mapped["Page"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Page", foreign_keys=[page_id]
    )
    category: Mapped["Category"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Category", foreign_keys=[category_id]
    )
