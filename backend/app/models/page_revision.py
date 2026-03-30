"""PageRevision 모델 — 문서 편집 이력 (불변 레코드)"""
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PageRevision(Base):
    """문서 편집 이력 — 한 번 생성되면 수정 불가 (불변 레코드)

    revision_number 컬럼 없음. 버전 식별은 id 사용.
    """

    __tablename__ = "page_revisions"

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
    # 조회 최적화용 비정규화 컬럼
    wiki_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("wikis.id"),
        nullable=False,
        index=True,
    )

    # 편집자 정보 — 로그인: editor_id, 비로그인: editor_ip
    editor_id: Mapped[int | None] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("users.id"),
        nullable=True,
    )
    # INET은 PostgreSQL 전용이므로 String(45)로 대체 (SQLite/MySQL 호환)
    editor_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)

    # 이 버전의 본문 전체 (나무마크 원문)
    content: Mapped[str] = mapped_column(Text, default="", nullable=False)

    # 편집 요약
    comment: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # 편집 플래그
    is_minor: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_bot: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # 용량 정보
    byte_size: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    byte_diff: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 이력 말소 플래그 (관리자 처리)
    is_suppressed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # 불변 레코드 — created_at만 존재 (updated_at 없음)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # 관계
    page: Mapped["Page"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Page",
        back_populates="revisions",
        foreign_keys=[page_id],
    )
    editor: Mapped["User | None"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "User", back_populates="page_revisions", foreign_keys=[editor_id]
    )
