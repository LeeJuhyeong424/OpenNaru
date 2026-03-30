"""SearchIndex 모델 — 전문 검색 인덱스"""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class SearchIndex(Base):
    """전문 검색 인덱스 — PostgreSQL FTS 또는 Meilisearch 연동용

    search_vector (tsvector)는 PostgreSQL 전용이므로 일단 생략.
    """

    __tablename__ = "search_index"
    __table_args__ = (
        # 위키-문서 쌍은 유일
        UniqueConstraint("wiki_id", "page_id", name="uq_search_index_wiki_page"),
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
    page_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("pages.id"),
        nullable=False,
        index=True,
    )

    # 검색용 플레인 텍스트
    title: Mapped[str] = mapped_column(Text, default="", nullable=False)
    content_plain: Mapped[str] = mapped_column(Text, default="", nullable=False)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # 관계
    wiki: Mapped["Wiki"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Wiki", foreign_keys=[wiki_id]
    )
    page: Mapped["Page"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Page", foreign_keys=[page_id]
    )
