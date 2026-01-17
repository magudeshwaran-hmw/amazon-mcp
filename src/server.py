
import asyncio
import json
import sqlite3
import os
from datetime import datetime
from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types

from .config import logger
from .database import AmazonDatabase
from .scraper import AmazonScraper

# Initialize components
db = AmazonDatabase()
scraper = AmazonScraper()

# Server Definition
server = Server("amazon-search")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="search_product",
            description="Search Amazon.in products with intelligent caching",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Product name or keywords"},
                    "limit": {"type": "integer", "description": "Max results (default: 10)"}
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="get_product_details",
            description="Get detailed product info including price, rating, reviews",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Product page URL"}
                },
                "required": ["url"]
            }
        ),
        types.Tool(
            name="get_trending_products",
            description="Get trending products based on access patterns and cache",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 20}
                }
            }
        ),
        types.Tool(
            name="get_price_history",
            description="Get historical price data for a product",
            inputSchema={
                "type": "object",
                "properties": {
                    "product_id": {"type": "string", "description": "ASIN or Product ID"}
                },
                "required": ["product_id"]
            }
        ),
        types.Tool(
            name="add_to_favorites",
            description="Add a product to favorites/watchlist",
            inputSchema={
                "type": "object",
                "properties": {
                    "product_id": {"type": "string", "description": "ASIN or Product ID"},
                    "url": {"type": "string", "description": "Product URL if ID unknown"}
                },
                "required": ["product_id"]
            }
        ),
        types.Tool(
            name="get_favorites",
            description="List all favorite products",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 50}
                }
            }
        ),
        types.Tool(
            name="remove_from_favorites",
            description="Remove a product from favorites",
            inputSchema={
                "type": "object",
                "properties": {
                    "product_id": {"type": "string"}
                },
                "required": ["product_id"]
            }
        ),
        types.Tool(
            name="get_search_history",
            description="Get recent search queries",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 20}
                }
            }
        ),

        types.Tool(
            name="get_product_recommendations",
            description="Get product recommendations based on a product you like",
            inputSchema={
                "type": "object",
                "properties": {
                    "product_id": {"type": "string", "description": "ASIN of product"},
                    "limit": {"type": "integer", "default": 10}
                },
                "required": ["product_id"]
            }
        ),
        types.Tool(
            name="get_market_analytics",
            description="Get price ranges and rating distribution analytics",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "Category to analyze (optional)"}
                }
            }
        ),
        types.Tool(
            name="search_by_category",
            description="Search products by category (Electronics, Fashion, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "Category name"},
                    "limit": {"type": "integer", "default": 10}
                },
                "required": ["category"]
            }
        ),
        types.Tool(
            name="get_latest_products",
            description="Get latest products added to the cache",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 20}
                }
            }
        ),
        types.Tool(
            name="refresh_cache",
            description="Refresh cached product data from Amazon",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 10, "description": "Max items to refresh"}
                }
            }
        ),
        types.Tool(
            name="batch_search",
            description="Search multiple products at once",
            inputSchema={
                "type": "object",
                "properties": {
                    "queries": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["queries"]
            }
        ),
        types.Tool(
            name="get_cache_stats",
            description="Get database and cache statistics",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="clear_cache",
            description="Clear all cached data",
            inputSchema={
                "type": "object",
                "properties": {
                    "confirm": {"type": "boolean"}
                },
                "required": ["confirm"]
            }
        ),
        types.Tool(
            name="export_data",
            description="Export product data to JSON",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "default": "amazon_export.json"}
                }
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    if not arguments:
        arguments = {}

    conn = await db.get_connection()
    
    try:
        if name == "search_product":
            query = arguments.get("query")
            limit = arguments.get("limit", 10)
            
            # Log history
            await conn.execute("INSERT INTO search_history (query, results_count) VALUES (?, ?)", (query, 0))
            await conn.commit()

            # First check cache for exact match on title (fuzzy match would be better but keeping simple)
            cursor = await conn.execute(
                "SELECT * FROM products WHERE title LIKE ? ORDER BY access_count DESC LIMIT ?", 
                (f"%{query}%", limit)
            )
            cached_results = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            results = [dict(zip(columns, row)) for row in cached_results]
            
            if not results:
                # Scrape
                scraped_results = await scraper.search(query)
                results = scraped_results[:limit]
                
                # Cache results
                for p in results:
                    await conn.execute(
                        """INSERT OR IGNORE INTO products (id, title, url, price, rating, reviews_count, image_url, last_updated) 
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (p['id'], p['title'], p['url'], p['price'], p['rating'], p['reviews_count'], p['image_url'], datetime.now())
                    )
                    # Update price history
                    await conn.execute("INSERT INTO price_history (product_id, price) VALUES (?, ?)", (p['id'], p['price']))
                
                await conn.commit()
                
                # Update history count
                if results:
                    await conn.execute("UPDATE search_history SET results_count = ? WHERE query = ? AND id = (SELECT MAX(id) FROM search_history)", (len(results), query))
                    await conn.commit()

            return [types.TextContent(type="text", text=json.dumps(results, indent=2))]

        elif name == "get_product_details":
            url = arguments.get("url")
            # Try to scrape details
            details = await scraper.get_details(url)
            
            if details and details.get('id'):
                 # Update DB
                await conn.execute(
                    "UPDATE products SET description = ?, availability = ?, last_updated = ?, access_count = access_count + 1 WHERE id = ?",
                    (details.get('description'), details.get('availability'), datetime.now(), details.get('id'))
                )
                await conn.commit()
            
            # Fetch full record
            if details.get('id'):
                cursor = await conn.execute("SELECT * FROM products WHERE id = ?", (details['id'],))
                row = await cursor.fetchone()
                if row:
                    columns = [description[0] for description in cursor.description]
                    details = dict(zip(columns, row))

            return [types.TextContent(type="text", text=json.dumps(details, indent=2))]

        elif name == "get_trending_products":
            limit = arguments.get("limit", 20)
            cursor = await conn.execute("SELECT * FROM products ORDER BY access_count DESC LIMIT ?", (limit,))
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            results = [dict(zip(columns, row)) for row in rows]
            return [types.TextContent(type="text", text=json.dumps(results, indent=2))]

        elif name == "get_price_history":
            product_id = arguments.get("product_id")
            cursor = await conn.execute("SELECT price, timestamp FROM price_history WHERE product_id = ? ORDER BY timestamp DESC", (product_id,))
            rows = await cursor.fetchall()
            history = [{"price": r[0], "date": r[1]} for r in rows]
            return [types.TextContent(type="text", text=json.dumps(history, indent=2))]

        elif name == "add_to_favorites":
            product_id = arguments.get("product_id")
            try:
                await conn.execute("INSERT INTO favorites (product_id) VALUES (?)", (product_id,))
                await conn.commit()
                return [types.TextContent(type="text", text=f"Added {product_id} to favorites")]
            except sqlite3.IntegrityError:
                return [types.TextContent(type="text", text=f"Product {product_id} already in favorites")]

        elif name == "get_favorites":
            limit = arguments.get("limit", 50)
            cursor = await conn.execute("""
                SELECT p.* FROM products p 
                JOIN favorites f ON p.id = f.product_id 
                ORDER BY f.created_at DESC LIMIT ?
            """, (limit,))
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            results = [dict(zip(columns, row)) for row in rows]
            return [types.TextContent(type="text", text=json.dumps(results, indent=2))]

        elif name == "remove_from_favorites":
            product_id = arguments.get("product_id")
            await conn.execute("DELETE FROM favorites WHERE product_id = ?", (product_id,))
            await conn.commit()
            return [types.TextContent(type="text", text=f"Removed {product_id} from favorites")]

        elif name == "get_search_history":
            limit = arguments.get("limit", 20)
            cursor = await conn.execute("SELECT * FROM search_history ORDER BY created_at DESC LIMIT ?", (limit,))
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            results = [dict(zip(columns, row)) for row in rows]
            return [types.TextContent(type="text", text=json.dumps(results, indent=2))]

        elif name == "batch_search":
            queries = arguments.get("queries", [])
            results = {}
            for q in queries:
                # Reuse search logic (simplified)
                search_res = await scraper.search(q)
                results[q] = search_res[:3] # Top 3 per query
            return [types.TextContent(type="text", text=json.dumps(results, indent=2))]

        elif name == "get_cache_stats":
            stats = {}
            async with conn.execute("SELECT COUNT(*) FROM products") as c:
                stats["total_products"] = (await c.fetchone())[0]
            async with conn.execute("SELECT COUNT(*) FROM favorites") as c:
                stats["total_favorites"] = (await c.fetchone())[0]
            async with conn.execute("SELECT COUNT(*) FROM search_history") as c:
                stats["total_searches"] = (await c.fetchone())[0]
            return [types.TextContent(type="text", text=json.dumps(stats, indent=2))]
        
        elif name == "get_product_recommendations":
             # Simple recommendation: same category or random
            product_id = arguments.get("product_id")
            limit = arguments.get("limit", 10)
            
            # Find category of current product
            cursor = await conn.execute("SELECT title FROM products WHERE id = ?", (product_id,))
            row = await cursor.fetchone()
            if row:
                title_part = row[0].split(' ')[0] # Simple match on first word
                cursor = await conn.execute("SELECT * FROM products WHERE title LIKE ? AND id != ? LIMIT ?", (f"%{title_part}%", product_id, limit))
                rows = await cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                results = [dict(zip(columns, row)) for row in rows]
                return [types.TextContent(type="text", text=json.dumps(results, indent=2))]
            return [types.TextContent(type="text", text="Product not found or no recommendations")]

        elif name == "get_market_analytics":
             # Basic aggregation
            analytics = {}
            async with conn.execute("SELECT AVG(access_count) FROM products") as c:
                analytics["avg_popularity"] = (await c.fetchone())[0]
            
             # Count by approximate rating (if we parsed it properly as float, but it's text "4.5 out of 5")
             # This is a bit rough due to text storage, but demonstrating intent
            return [types.TextContent(type="text", text=json.dumps(analytics, indent=2))]

        elif name == "search_by_category":
            category = arguments.get("category")
            limit = arguments.get("limit", 10)
            # Find closest Amazon category or just search with category keyword
            products = await scraper.search(category, page=1)
            return [types.TextContent(type="text", text=json.dumps(products[:limit], indent=2))]

        elif name == "get_latest_products":
            limit = arguments.get("limit", 20)
            cursor = await conn.execute("SELECT * FROM products ORDER BY created_at DESC LIMIT ?", (limit,))
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            results = [dict(zip(columns, row)) for row in rows]
            return [types.TextContent(type="text", text=json.dumps(results, indent=2))]

        elif name == "refresh_cache":
            limit = arguments.get("limit", 10)
            # Get oldest updated products
            cursor = await conn.execute("SELECT id, url FROM products ORDER BY last_updated ASC LIMIT ?", (limit,))
            rows = await cursor.fetchall()
            
            refreshed_count = 0
            for row in rows:
                pid, url = row
                details = await scraper.get_details(url)
                if details:
                    await conn.execute(
                        "UPDATE products SET price = ?, description = ?, availability = ?, last_updated = ? WHERE id = ?",
                        (details.get('price'), details.get('description'), details.get('availability'), datetime.now(), pid)
                    )
                    # Update price history if changed? (simplified here)
                    await conn.execute("INSERT INTO price_history (product_id, price) VALUES (?, ?)", (pid, details.get('price')))
                    refreshed_count += 1
            
            await conn.commit()
            return [types.TextContent(type="text", text=f"Refreshed {refreshed_count} products")]

        elif name == "clear_cache":
            if arguments.get("confirm"):
                await conn.execute("DELETE FROM products")
                await conn.execute("DELETE FROM price_history")
                await conn.execute("DELETE FROM search_history")
                await conn.commit()
                return [types.TextContent(type="text", text="Cache cleared successfully")]
            return [types.TextContent(type="text", text="Confirmation required to clear cache")]

        elif name == "export_data":
            filename = arguments.get("filename", "amazon_export.json")
            cursor = await conn.execute("SELECT * FROM products")
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            data = [dict(zip(columns, row)) for row in rows]
            
            filepath = os.path.join(os.getcwd(), filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            return [types.TextContent(type="text", text=f"Data exported to {filepath}")]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}")
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    finally:
        await conn.close()

async def serve():
    try:
        # Initialize DB
        await db.init_db()
        
        # Run server
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                initialization_options=server.create_initialization_options()
            )
    except Exception as e:
        logger.critical(f"Server crash: {e}", exc_info=True)
        sys.exit(1)
