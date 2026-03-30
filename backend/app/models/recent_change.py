"""RecentChange 모델 — 최근 변경 로그"""
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class RecentChange(Base):
    """최근 변경 로그 — 위키 전체의 변경 이력 집계"""

    __tablename__ = "recent_changes"

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

    # 변경 타입: edit / new / move / delete / upload
    change_type: Mapped[str] = mapped_column(String(20), nullable=False)

    # 관련 문서 (NULL = 문서 무관 변경)
    page_id: Mapped[int | None] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("pages.id"),
        nullable=True,
    )
    # 문서 제목 스냅샷 (문서 삭제 후에도 제목 보존)
    page_title: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # 관련 revision
    revision_id: Mapped[int | None] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("page_revisions.id"),
        nullable=True,
    )

    # 행위자 (NULL = 비로그인)
    actor_id: Mapped[int | None] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("users.id"),
        nullable=True,
    )
    # 비로그인 행위자 이름 스냅샷
    actor_name: Mapped[str | None] = mapped_column(String(40), nullable=True)

    comment: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_minor: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_bot: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    byte_diff: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 불변 레코드 — created_at만 존재
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    # 관계
    wiki: Mapped["Wiki"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Wiki", foreign_keys=[wiki_id]
    )
    page: Mapped["Page | None"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Page", foreign_keys=[page_id]
    )
    revision: Mapped["PageRevision | None"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "PageRevision", foreign_keys=[revision_id]
    )
    actor: Mapped["User | None"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "User", foreign_keys=[actor_id]
    )
