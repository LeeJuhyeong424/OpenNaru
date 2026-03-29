"""스키마 패키지"""
from app.schemas.common import PaginatedResponse
from app.schemas.page import PageCreate, PageResponse, PageRevisionResponse, PageUpdate
from app.schemas.wiki import WikiCreate, WikiListResponse, WikiResponse, WikiUpdate

__all__ = [
    "PaginatedResponse",
    "WikiCreate",
    "WikiUpdate",
    "WikiResponse",
    "WikiListResponse",
    "PageCreate",
    "PageUpdate",
    "PageResponse",
    "PageRevisionResponse",
]
