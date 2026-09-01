"""
backend/alembic/env.py
Alembic migration environment — async-compatible with SQLAlchemy 2.0.

Loads DATABASE_URL from the application settings (not from alembic.ini),
so a single .env file controls everything.
"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# ── Alembic config object ─────────────────────────────────────────────────────
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ── Import all models so Alembic detects them ─────────────────────────────────
# Add new models here as phases are completed.
from app.db.session import Base  # noqa: F401 — registers metadata
from app.models.resume_chunk import ResumeChunk  # noqa: F401

target_metadata = Base.metadata

# ── Load DATABASE_URL from application settings ───────────────────────────────
from app.core.config import get_settings  # noqa: E402

_settings = get_settings()

# Alembic needs a sync URL even with async engine_from_config
# We replace asyncpg with psycopg2 for Alembic's sync offline mode,
# but for online (async) mode we use the async URL directly.
_async_url = _settings.DATABASE_URL  # postgresql+asyncpg://...


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (no live DB connection needed)."""
    context.configure(
        url=_async_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # pgvector type comparison
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode using an async engine."""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = _async_url

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Entry point for online migration mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
