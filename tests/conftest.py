import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.database import Base, get_db_session
from app.jobs.router import get_storage
from app.main import create_app


class FakeStorage:
    def upload_bytes(self, data: bytes, key: str, content_type: str = "application/octet-stream") -> None:
        return None

    def generate_presigned_url(self, key: str) -> str:
        return f"https://example.test/{key}"


@pytest.fixture
def client():
    app = create_app()
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    test_session = async_sessionmaker(bind=test_engine, autoflush=False, expire_on_commit=False)

    async def override_db():
        async with test_session() as session:
            yield session

    async def init_models() -> None:
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    import asyncio

    asyncio.get_event_loop().run_until_complete(init_models())

    app.dependency_overrides[get_db_session] = override_db
    app.dependency_overrides[get_storage] = lambda: FakeStorage()

    with TestClient(app) as test_client:
        yield test_client
