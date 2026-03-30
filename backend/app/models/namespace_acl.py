"""NamespaceAcl 모델 — 네임스페이스 단위 ACL"""
from sqlalchemy import BigInteger, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class NamespaceAcl(Base):
    """네임스페이스 단위 ACL — 위키의 특정 네임스페이스에 대한 액션별 접근 등급"""

    __tablename__ = "namespace_acls"
    __table_args__ = (
        # 한 위키의 같은 네임스페이스/액션 조합은 하나의 ACL만 허용
        UniqueConstraint(
            "wiki_id", "namespace", "action", name="uq_namespace_acls_wiki_ns_action"
        ),
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

    # 네임스페이스: main / talk / user / file / template / help
    namespace: Mapped[str] = mapped_column(String(30), nullable=False)

    # 액션: read / edit / discuss / move / delete
    action: Mapped[str] = mapped_column(String(20), nullable=False)

    # 허용 최소 등급: blocked/anonymous/member/autoconf/admin/sysadmin
    acl_value: Mapped[str] = mapped_column(
        String(20), default="anonymous", nullable=False
    )

    # 관계
    wiki: Mapped["Wiki"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Wiki", foreign_keys=[wiki_id]
    )
