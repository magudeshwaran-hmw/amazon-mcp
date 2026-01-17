# Amazon MCP Server - Enhanced Edition

A high-performance MCP (Model Context Protocol) server for searching Amazon India products with advanced features, fast caching, and many powerful tools.

## 🚀 Features

- 🔍 **Fast Product Search** - Search Amazon products with intelligent caching
- 📦 **Product Details** - Get price, rating, reviews, images, descriptions
- 🔥 **Trending Products** - Discover popular products based on access patterns
- 🏷️ **Category-based Search** - Filter by categories (electronics, etc.)
- 💸 **Price Tracking** - Track historical price changes
- ⭐ **Favorites System** - Save your favorite products
- 📜 **Search History** - Track your search history
- 🔄 **Batch Operations** - Search multiple products at once
- 📤 **Export/Import** - Export product data to JSON format
- 🎯 **Recommendations** - Get product recommendations (simulated)
- ⚡ **High Performance** - Async operations, connection pooling
- 💾 **Smart Caching** - SQLite database with intelligent caching strategies
- 📈 **Statistics** - Comprehensive cache and usage statistics

## 📦 Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## 🎯 Usage

### Running the MCP Server

The server uses stdio transport. Configure it in your [MCP client](https://github.com/modelcontextprotocol/servers) (like Cursor):

```bash
python main.py
```

### Testing the Server

Test functionality:

```bash
python test_server.py
```

### Configuring in Cursor/Claude Desktop

Add to your MCP settings (`%APPDATA%\Cursor\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json` on Windows):

```json
{
  "mcpServers": {
    "amazon-search": {
      "command": "python",
      "args": ["C:\\Users\\Magudesh\\Desktop\\mcp\\mcp2\\main.py"],
      "cwd": "C:\\Users\\Magudesh\\Desktop\\mcp\\mcp2"
    }
  }
}
```

**Note:** Update paths to match your installation directory.

## 🛠️ Available Tools

### 1. `search_product`
Search for Amazon products by name.

**Parameters:**
- `query` (string, required): Product name/keywords
- `limit` (integer, optional): Max results (default: 10)

### 2. `get_product_details`
Get detailed information including price, rating, and description.

**Parameters:**
- `url` (string, required): Product page URL

### 3. `get_trending_products`
Get trending products based on access count.

### 4. `get_price_history`
Get historical price data.

**Parameters:**
- `product_id` (string, required): ASIN or Product ID

### 5. `add_to_favorites`
Add a product to your favorites list.

**Parameters:**
- `product_id` (string, required): ASIN

### 6. `get_favorites`
Get all your favorite products.

### 7. `remove_from_favorites`
Remove a product from favorites.

### 8. `get_search_history`
Get your recent search history.

### 9. `batch_search`
Search for multiple products at once.

**Example:**
```json
{
  "queries": ["iPhone 15", "Samsung S24"]
}
```

### 10. `get_cache_stats`
Get database statistics.

### 11. `export_data`
Export products to JSON.

### 12. `clear_cache`
Clear all cached data.

## ⚡ Performance Features

### Async Operations
- All database operations use `aiosqlite`
- Parallel scraping where possible
- Connection pooling for HTTP requests

### Smart Caching
- Database caching with access tracking
- Price history tracking

## 📊 Database Schema

### `products` Table
- `id`: ASIN
- `title`: Product Title
- `price`: Current Price
- `rating`: Star Rating
- `reviews_count`: Number of reviews
- etc.

## 📝 Notes

- Scrapes `amazon.in`
- Uses User-Agent rotation to avoid blocking
- Caches results for 1 hour by default
