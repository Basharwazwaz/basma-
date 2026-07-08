import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.main import app
from app.db.base import Base
from app.db.session import get_db

# Use in-memory sqlite for tests
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM, ARRAY, UUID as PG_UUID
from sqlalchemy import VARCHAR, JSON, String
import sqlalchemy.types as types

@compiles(PG_ENUM, 'sqlite')
def compile_pg_enum(element, compiler, **kw):
    return "VARCHAR"

@compiles(ARRAY, 'sqlite')
def compile_array(element, compiler, **kw):
    return "JSON"

@compiles(PG_UUID, 'sqlite')
def compile_uuid(element, compiler, **kw):
    return "VARCHAR"

@compiles(types.Enum, 'sqlite')
def compile_enum(element, compiler, **kw):
    return "VARCHAR"

TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        # Drop all tables after tests
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def test_db_session():
    async with TestingSessionLocal() as session:
        yield session
