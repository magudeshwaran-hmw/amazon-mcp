
import asyncio
from src.database import AmazonDatabase
from src.scraper import AmazonScraper

async def test_search():
    print("\n--- Testing Search ---")
    scraper = AmazonScraper()
    results = await scraper.search("laptop", page=1)
    print(f"Found {len(results)} results")
    if results:
        print(f"First result: {results[0]['title']} - {results[0]['price']}")
    return results

async def test_db():
    print("\n--- Testing Database ---")
    db = AmazonDatabase()
    await db.init_db()
    conn = await db.get_connection()
    
    # Test Insert
    await conn.execute(
        "INSERT OR IGNORE INTO products (id, title, url, price) VALUES (?, ?, ?, ?)",
        ("TEST001", "Test Product", "http://example.com", "999")
    )
    await conn.commit()
    
    # Test Select
    cursor = await conn.execute("SELECT * FROM products WHERE id = 'TEST001'")
    row = await cursor.fetchone()
    print(f"Database item: {row}")
    await conn.close()

async def main():
    await test_db()
    # Uncomment to test actual scraping (might fail if IP blocked or network issues)
    # await test_search()

if __name__ == "__main__":
    asyncio.run(main())
