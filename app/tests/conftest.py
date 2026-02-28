from app.main import app as fastapi_app
from app.database import Base, async_session_maker
from app.config import settings
from httpx import ASGITransport, AsyncClient
from fastapi.testclient import TestClient
import pytest_asyncio
import pytest
from datetime import date, datetime
import json
import asyncio
import os


@pytest.fixture(scope='session', autouse=True)
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture(scope='session', autouse=True)
async def prepare_database():
    import asyncpg
    from sqlalchemy.pool import NullPool
    from sqlalchemy.ext.asyncio import create_async_engine

    try:
        sys_conn = await asyncpg.connect(
            user=settings.TEST_DB_USER,
            password=settings.TEST_DB_PASS,
            host=settings.TEST_DB_HOST,
            port=settings.TEST_DB_PORT,
            database="postgres",
        )
        db_exists = await sys_conn.fetchval(
            f"SELECT 1 FROM pg_database WHERE datname='{settings.TEST_DB_NAME}'"
        )
        if not db_exists:
            await sys_conn.execute(f'CREATE DATABASE {settings.TEST_DB_NAME}')
        await sys_conn.close()
    except Exception as e:
        print(f"DB creation skipped: {e}")

    test_engine = create_async_engine(
        settings.TEST_DATABASE_URL,
        poolclass=NullPool,
    )

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Apply seed data (roles, resources, rules, admin user)
    with open("seed.sql", "r", encoding="utf-8") as f:
        sql_script = f.read()

    conn = await asyncpg.connect(
        user=settings.TEST_DB_USER,
        password=settings.TEST_DB_PASS,
        host=settings.TEST_DB_HOST,
        port=settings.TEST_DB_PORT,
        database=settings.TEST_DB_NAME,
    )
    if "```sql" in sql_script:
        sql_commands = sql_script.split("```sql")[1].split("```")[0]
        await conn.execute(sql_commands)
    await conn.close()

    # Ensure admin password hash matches current auth implementation
    from sqlalchemy import update  # local import to avoid circulars at module load
    from app.users.models import Users
    from app.users.auth import get_password_hash

    async with async_session_maker() as session:
        stmt = (
            update(Users)
            .where(Users.email == "admin@admin.com")
            .values(password_hash=get_password_hash("admin123"))
        )
        await session.execute(stmt)
        await session.commit()

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


fastapi_transport = ASGITransport(app=fastapi_app)


@pytest_asyncio.fixture(scope='function')
async def ac():
    async with AsyncClient(transport=fastapi_transport, base_url='http://test/api/v1',) as ac:
        yield ac


@pytest_asyncio.fixture(scope='function')
async def session():
    async with async_session_maker() as session:
        yield session


@pytest_asyncio.fixture(scope='function')
async def authenticated_ac():
    async with AsyncClient(transport=fastapi_transport, base_url='http://test/api/v1',) as ac:
        response = await ac.post('/users/auth/login', json={
            'email': 'admin@admin.com',
            'password': 'admin123'
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        yield ac


@pytest_asyncio.fixture(scope='function')
async def admin_client(authenticated_ac: AsyncClient):
    yield authenticated_ac
