"""테스트 공통 픽스처 — SQLite in-memory DB 기반 통합 테스트 환경"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# 모든 모델을 먼저 임포트해야 Base.metadata에 테이블 정보가 등록됨
import app.models  # noqa: F401
from app.core.database import Base, get_db
from app.main import app

# SQLite in-memory DB URL
# StaticPool을 사용해야 동일 연결을 재사용하여 테이블이 유지됨
SQLITE_URL = "sqlite://"


@pytest.fixture
def engine():
    """테스트용 SQLite in-memory 엔진 — StaticPool로 동일 연결 공유"""
    _engine = create_engine(
        SQLITE_URL,
        connect_args={"check_same_thread": False},
        # StaticPool: 모든 커넥션 요청에 동일한 연결 객체 반환 → in-memory DB 공유
        poolclass=StaticPool,
    )
    # 등록된 모든 테이블 생성
    Base.metadata.create_all(bind=_engine)
    yield _engine
    # 테스트 후 테이블 전부 삭제
    Base.metadata.drop_all(bind=_engine)
    _engine.dispose()


@pytest.fixture
def db_session(engine):
    """테스트용 DB 세션 — 함수 스코프"""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    """FastAPI TestClient — get_db 의존성을 테스트 세션으로 오버라이드"""

    def override_get_db():
        """테스트 DB 세션을 주입하는 의존성 오버라이드"""
        try:
            yield db_session
        finally:
            pass  # 세션 닫기는 db_session 픽스처가 담당

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    # 테스트 종료 후 오버라이드 해제
    app.dependency_overrides.clear()
