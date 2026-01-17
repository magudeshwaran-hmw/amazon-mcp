# Amazon MCP Server - Enhanced Edition

A high-performance MCP (Model Context Protocol) server for searching Amazon India products with advanced features, fast caching, and many powerful tools.

## 🚀 Quick Start (Recommended)

Run instantly with `npx` (no installation required):

```bash
npx -y @magudeshwaran-hmw/amazon-mcp-server
```

## 🛠️ Configuration

Add this to your MCP settings (Cursor, Claude Desktop, etc.):

```json
{
  "mcpServers": {
    "amazon-search": {
      "command": "npx",
      "args": ["-y", "@magudeshwaran-hmw/amazon-mcp-server"]
    }
  }
}
```

> **Note**: Requires Python to be installed and available in your system PATH.

## ✨ Features

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

## 📦 Local Development

If you want to run or modify the code locally:

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Server**:
   ```bash
   python main.py
   ```

3. **Test Functionality**:
   ```bash
   python test_server.py
   ```

## 🛠️ Available Tools

### 1. `search_product`
Search for Amazon products by name.
- `query` (string): Product name
- `limit` (int): Max results

### 2. `get_product_details`
Get detailed information.
- `url` (string): Product URL

### 3. `get_trending_products`
Get popular products.

### 4. `get_price_history`
- `product_id` (string): ASIN

### 5. `add_to_favorites` / `remove_from_favorites`
Manage your wishlist.

### 6. `batch_search`
Search multiple queries at once.

### 7. `export_data`
Export database to JSON.

## ⚡ Tech Stack
- **Python**: Core logic (mcp, aiosqlite, beautifulsoup4)
- **Node.js**: Distribution wrapper (npx)
- **SQLite**: Local caching
