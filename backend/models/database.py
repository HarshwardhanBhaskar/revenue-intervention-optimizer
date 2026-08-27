"""
Database connection and session management.

Uses SQLAlchemy 2.0 async engine for FastAPI compatibility.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool
from sqlalchemy import create_engine
import logging
from config import get_settings

logger = logging.getLogger("rio.database")


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


# Async engine for FastAPI
_async_engine = None
_async_session_factory = None

# Sync engine for ML scripts and data loading
_sync_engine = None


def get_async_engine():
    global _async_engine
    if _async_engine is None:
        settings = get_settings()
        db_url = settings.database_url
        
        # Normalize URL for asyncpg
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif db_url.startswith("postgresql://") and "+asyncpg" not in db_url:
            db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

        if "postgresql" in db_url:
            # When connecting via PgBouncer / Supavisor transaction mode,
            # statement caching must be disabled and NullPool avoids connection state issues
            connect_args = {
                "statement_cache_size": 0,
                "prepared_statement_cache_size": 0,
            }
            _async_engine = create_async_engine(
                db_url,
                echo=False,
                poolclass=NullPool,
                connect_args=connect_args,
            )
        else:
            _async_engine = create_async_engine(
                db_url,
                echo=False,
            )
    return _async_engine


def get_sync_engine():
    global _sync_engine
    if _sync_engine is None:
        settings = get_settings()
        db_url = settings.database_sync_url
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)

        if "postgresql" in db_url:
            _sync_engine = create_engine(
                db_url,
                echo=False,
                pool_size=5,
                pool_pre_ping=True,
            )
        else:
            _sync_engine = create_engine(
                db_url,
                echo=False,
            )
    return _sync_engine


def get_async_session_factory():
    global _async_session_factory
    if _async_session_factory is None:
        _async_session_factory = async_sessionmaker(
            bind=get_async_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _async_session_factory


async def get_db() -> AsyncSession:
    """FastAPI dependency for database sessions."""
    session_factory = get_async_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Create all tables. Called on startup."""
    try:
        engine = get_async_engine()
        async with engine.begin() as conn:
            # Import all models so they're registered with Base
            from models import customer, order, payment, recovery_opportunity  # noqa
            from models import recovery_action, recovery_outcome, policy  # noqa
            from models import approval, audit_event, experiment, model_prediction  # noqa
            from models import merchant, payment_event  # noqa
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database schema initialized successfully")
    except Exception as e:
        logger.warning(
            f"Database init_db warning (tables may already exist or running behind PgBouncer): {e}"
        )

