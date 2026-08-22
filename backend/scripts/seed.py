"""
Seed Script — Run via python scripts/seed.py
"""

import asyncio
import sys
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models.database import get_async_session_factory, init_db
from services.seed_service import SeedService


async def main():
    print("=" * 60)
    print("Initializing Database and Seeding Demo Data")
    print("=" * 60)
    
    # 1. Initialize schema
    print("[1/2] Initializing tables...")
    await init_db()
    print("  -> Tables initialized.")

    # 2. Seed data
    print("[2/2] Seeding data...")
    session_factory = get_async_session_factory()
    async with session_factory() as session:
        merchant = await SeedService.seed_database(session)
        print(f"  -> Merchant created: {merchant.name} (ID: {merchant.id})")

    print("\n[OK] Database successfully initialized and seeded.")


if __name__ == "__main__":
    asyncio.run(main())
