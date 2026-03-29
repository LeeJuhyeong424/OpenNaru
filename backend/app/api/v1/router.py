from fastapi import APIRouter

from app.api.v1.endpoints import pages, wikis

api_router = APIRouter()

# 위키 CRUD
api_router.include_router(wikis.router, prefix="/wikis", tags=["위키"])
# 문서 CRUD (prefix="/wikis"로 등록 — 내부적으로 /{wiki_slug}/pages/... 경로 사용)
api_router.include_router(pages.router, prefix="/wikis", tags=["문서"])
