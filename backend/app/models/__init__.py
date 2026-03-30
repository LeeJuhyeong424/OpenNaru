"""모델 패키지 — 모든 ORM 모델 임포트 (Alembic 마이그레이션 감지용)"""
from app.models.block import Block
from app.models.category import Category
from app.models.discussion import Discussion
from app.models.discussion_comment import DiscussionComment
from app.models.edit_request import EditRequest
from app.models.file import File
from app.models.namespace_acl import NamespaceAcl
from app.models.notification import Notification
from app.models.page import Page
from app.models.page_acl import PageAcl
from app.models.page_category import PageCategory
from app.models.page_revision import PageRevision
from app.models.recent_change import RecentChange
from app.models.revision_suppression import RevisionSuppression
from app.models.search_index import SearchIndex
from app.models.user import User
from app.models.user_acl_override import UserAclOverride
from app.models.wiki import Wiki
from app.models.wiki_member import WikiMember

__all__ = [
    "User",
    "Wiki",
    "WikiMember",
    "Block",
    "Page",
    "PageRevision",
    "RevisionSuppression",
    "PageAcl",
    "NamespaceAcl",
    "UserAclOverride",
    "Category",
    "PageCategory",
    "File",
    "Discussion",
    "DiscussionComment",
    "EditRequest",
    "RecentChange",
    "SearchIndex",
    "Notification",
]
