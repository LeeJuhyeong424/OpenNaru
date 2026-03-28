"""공통 Pydantic 스키마 — 페이지네이션 등"""
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """페이지네이션 응답 래퍼"""

    items: list[T]
    total: int
    skip: int
    limit: int
