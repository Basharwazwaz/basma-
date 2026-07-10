import json
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import event, JSON as SA_JSON
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from app.main import app
from app.core.limiter import limiter
from app.db.base import Base
from app.db.session import get_db

# Use in-memory sqlite for tests
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM, UUID as PG_UUID, JSONB
from sqlalchemy import VARCHAR
import sqlalchemy.types as types


@compiles(PG_ENUM, 'sqlite')
def compile_pg_enum(element, compiler, **kw):
    return "VARCHAR"

@compiles(PG_ARRAY, 'sqlite')
def compile_array(element, compiler, **kw):
    return "VARCHAR"

@compiles(PG_UUID, 'sqlite')
def compile_uuid(element, compiler, **kw):
    return "VARCHAR"

@compiles(types.Enum, 'sqlite')
def compile_enum(element, compiler, **kw):
    return "VARCHAR"

@compiles(JSONB, 'sqlite')
def compile_jsonb(element, compiler, **kw):
    return "VARCHAR"


# Replace all PostgreSQL ARRAY columns with JSON for SQLite compatibility
# This must happen before table creation
for mapper in Base.registry.mappers:
    for col in mapper.c.values():
        if isinstance(col.type, PG_ARRAY):
            col.type = SA_JSON()
            col.type.cache_ok = True


TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db

# Disable rate limiting for tests
limiter.enabled = False


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture(autouse=True)
async def _clean_db():
    yield
    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())


@pytest_asyncio.fixture
async def test_db_session():
    async with TestingSessionLocal() as session:
        yield session
