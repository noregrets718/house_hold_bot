"""Database connection pool and CRUD operations."""

import asyncpg

from app.config import settings

pool: asyncpg.Pool | None = None


async def create_pool() -> asyncpg.Pool:
    """Create database connection pool."""
    global pool
    pool = await asyncpg.create_pool(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database=settings.db_name,
        min_size=1,
        max_size=10,
    )
    return pool


async def close_pool():
    """Close database connection pool."""
    global pool
    if pool:
        await pool.close()
        pool = None


# Donor operations

async def add_donor(last_name: str) -> bool:
    """Add a new donor. Returns True if added, False if already exists."""
    try:
        await pool.execute(
            "INSERT INTO donors (last_name) VALUES ($1)",
            last_name
        )
        return True
    except asyncpg.UniqueViolationError:
        return False


async def add_donors_many(last_names: list[str]) -> tuple[list[str], list[str]]:
    """Add multiple donors. Returns (added, already_existed) lists."""
    added = []
    existed = []
    for last_name in last_names:
        try:
            await pool.execute(
                "INSERT INTO donors (last_name) VALUES ($1)",
                last_name
            )
            added.append(last_name)
        except asyncpg.UniqueViolationError:
            existed.append(last_name)
    return added, existed


async def remove_donor(last_name: str) -> bool:
    """Remove donor by last name. Returns True if removed."""
    result = await pool.execute(
        "DELETE FROM donors WHERE last_name = $1",
        last_name
    )
    return result == "DELETE 1"


async def get_donor(last_name: str) -> dict | None:
    """Get donor by last name."""
    row = await pool.fetchrow(
        "SELECT id, last_name, created_at FROM donors WHERE last_name = $1",
        last_name
    )
    return dict(row) if row else None


async def get_all_donors() -> list[dict]:
    """Get all donors."""
    rows = await pool.fetch(
        "SELECT id, last_name, created_at FROM donors ORDER BY last_name"
    )
    return [dict(row) for row in rows]


# Payment operations

async def record_payment(donor_id: int, month: int, year: int, recorded_by: int) -> bool:
    """Record a payment. Returns True if recorded, False if already exists."""
    try:
        await pool.execute(
            "INSERT INTO payments (donor_id, month, year, recorded_by) VALUES ($1, $2, $3, $4)",
            donor_id, month, year, recorded_by
        )
        return True
    except asyncpg.UniqueViolationError:
        return False


async def delete_payment(donor_id: int, month: int, year: int) -> bool:
    """Delete a payment record. Returns True if deleted."""
    result = await pool.execute(
        "DELETE FROM payments WHERE donor_id = $1 AND month = $2 AND year = $3",
        donor_id, month, year
    )
    return result == "DELETE 1"


async def get_paid_donors(month: int, year: int) -> list[dict]:
    """Get donors who paid for a specific month."""
    rows = await pool.fetch(
        """
        SELECT d.id, d.last_name, p.recorded_at
        FROM donors d
        INNER JOIN payments p ON d.id = p.donor_id
        WHERE p.month = $1 AND p.year = $2
        ORDER BY d.last_name
        """,
        month, year
    )
    return [dict(row) for row in rows]


async def get_unpaid_donors(month: int, year: int) -> list[dict]:
    """Get donors who haven't paid for a specific month."""
    rows = await pool.fetch(
        """
        SELECT d.id, d.last_name
        FROM donors d
        WHERE d.id NOT IN (
            SELECT donor_id FROM payments
            WHERE month = $1 AND year = $2
        )
        ORDER BY d.last_name
        """,
        month, year
    )
    return [dict(row) for row in rows]


async def get_donor_history(donor_id: int) -> list[dict]:
    """Get payment history for a donor."""
    rows = await pool.fetch(
        """
        SELECT month, year, recorded_at, recorded_by
        FROM payments
        WHERE donor_id = $1
        ORDER BY year DESC, month DESC
        """,
        donor_id
    )
    return [dict(row) for row in rows]


# Admin operations

async def is_admin_in_db(telegram_id: int) -> bool:
    """Check if user is admin in database."""
    row = await pool.fetchrow(
        "SELECT 1 FROM admins WHERE telegram_id = $1",
        telegram_id
    )
    return row is not None


async def add_admin_to_db(telegram_id: int) -> bool:
    """Add admin to database."""
    try:
        await pool.execute(
            "INSERT INTO admins (telegram_id) VALUES ($1)",
            telegram_id
        )
        return True
    except asyncpg.UniqueViolationError:
        return False
