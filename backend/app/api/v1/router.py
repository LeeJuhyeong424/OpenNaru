from fastapi import APIRouter

api_router = APIRouter()

# 엔드포인트 추가 예시:
# from app.api.v1.endpoints import auth, wikis, pages
# api_router.include_router(auth.router, prefix="/auth", tags=["인증"])
# api_router.include_router(wikis.router, prefix="/wikis", tags=["위키"])
# api_router.include_router(pages.router, prefix="/wikis", tags=["문서"])
