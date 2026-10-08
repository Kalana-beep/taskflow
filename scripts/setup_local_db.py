"""Ensure local taskflow_db database exists in PostgreSQL."""

import asyncio
import asyncpg


async def main():
    conn = await asyncpg.connect("postgresql://postgres:postgres@localhost:5432/postgres")
    exists = await conn.fetchval("SELECT 1 FROM pg_database WHERE datname='taskflow_db'")
    if not exists:
        await conn.execute("CREATE DATABASE taskflow_db")
        print("Created database 'taskflow_db'")
    else:
        print("Database 'taskflow_db' already exists")
    await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
