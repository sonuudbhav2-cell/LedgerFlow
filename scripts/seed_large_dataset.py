import asyncio
import uuid
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.models.ledger import Account, JournalEntry, Posting

async def seed():
    async with AsyncSessionLocal() as session:
        print("Creating seed accounts...")
        asset = Account(id=uuid.uuid4(), name="Seed Asset", type="ASSET", currency="USD")
        revenue = Account(id=uuid.uuid4(), name="Seed Revenue", type="REVENUE", currency="USD")
        session.add_all([asset, revenue])
        await session.commit()

        print("Generating 100,000+ postings in batches...")
        batch_size = 5000
        total_entries = 50000  # 50k entries * 2 postings = 100k postings

        for i in range(0, total_entries, batch_size):
            entries = []
            postings = []
            for _ in range(batch_size):
                je_id = uuid.uuid4()
                entries.append(JournalEntry(id=je_id, description="Bulk Seed Tx"))
                amt = Decimal("10.00")
                postings.append(Posting(journal_entry_id=je_id, account_id=asset.id, amount=amt, direction="DEBIT"))
                postings.append(Posting(journal_entry_id=je_id, account_id=revenue.id, amount=amt, direction="CREDIT"))
            
            session.add_all(entries)
            session.add_all(postings)
            await session.commit()
            print(f"Inserted batch up to {i + batch_size} entries...")

if __name__ == "__main__":
    asyncio.run(seed())