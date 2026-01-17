
import httpx
import urllib.parse
import random
from datetime import datetime
from bs4 import BeautifulSoup
from typing import List, Dict
from .config import BASE_URL, USER_AGENTS, logger

class AmazonScraper:
    def __init__(self):
        self.client = httpx.AsyncClient(
            headers={
                "User-Agent": random.choice(USER_AGENTS),
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            },
            follow_redirects=True,
            timeout=30.0,
            verify=False # Often helps with local SSL issues, though use with caution in prod
        )

    async def search(self, query: str, page: int = 1) -> List[Dict]:
        url = f"{BASE_URL}/s?k={urllib.parse.quote(query)}&page={page}"
        logger.info(f"Searching: {url}")
        
        try:
            response = await self.client.get(url)
            # Response handling...
            if response.status_code != 200:
                logger.error(f"Failed to fetch search results: {response.status_code}")
                # Fallback or retry logic could go here
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            items = soup.select('.s-result-item[data-component-type="s-search-result"]')
            
            for item in items:
                try:
                    title_elem = item.select_one('h2 a span')
                    link_elem = item.select_one('h2 a')
                    price_elem = item.select_one('.a-price .a-offscreen')
                    rating_elem = item.select_one('.a-icon-star-small .a-icon-alt')
                    reviews_elem = item.select_one('.a-size-base.s-underline-text')
                    image_elem = item.select_one('.s-image')
                    
                    if not title_elem or not link_elem:
                        continue

                    product = {
                        'id': item.get('data-asin'),
                        'title': title_elem.text.strip(),
                        'url': BASE_URL + link_elem['href'] if not link_elem['href'].startswith('http') else link_elem['href'],
                        'price': price_elem.text.strip() if price_elem else "N/A",
                        'rating': rating_elem.text.strip().split(' out')[0] if rating_elem else "N/A",
                        'reviews_count': reviews_elem.text.strip() if reviews_elem else "0",
                        'image_url': image_elem['src'] if image_elem else "",
                        'source': 'amazon.in'
                    }
                    results.append(product)
                except Exception as e:
                    logger.error(f"Error parsing item: {e}")
                    continue
                    
            return results
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []

    async def get_details(self, product_url: str) -> Dict:
        logger.info(f"Fetching details: {product_url}")
        try:
            response = await self.client.get(product_url)
            if response.status_code != 200:
                return {}
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract basic details
            title_elem = soup.select_one('#productTitle')
            price_elem = soup.select_one('.a-price .a-offscreen') or soup.select_one('#priceblock_ourprice') or soup.select_one('#priceblock_dealprice')
            
            # Detailed description - scraping simplified for brevity
            description_elem = soup.select_one('#feature-bullets')
            availability_elem = soup.select_one('#availability')
            
            # ASIN from URL or page
            asin = ""
            if '/dp/' in product_url:
                parts = product_url.split('/dp/')
                if len(parts) > 1:
                    asin = parts[1].split('/')[0]
            
            return {
                'id': asin,
                'title': title_elem.text.strip() if title_elem else "Unknown",
                'price': price_elem.text.strip() if price_elem else "N/A",
                'description': description_elem.text.strip() if description_elem else "",
                'availability': availability_elem.text.strip() if availability_elem else "Unknown",
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Details error: {e}")
            return {}

    async def get_bestsellers(self, category: str = "electronics") -> List[Dict]:
        return []
