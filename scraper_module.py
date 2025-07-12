import asyncio
import aiohttp
import re
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import random
import time

logger = logging.getLogger(__name__)


class SneakerScraper:
    def __init__(self):
        self.base_url = "https://www.ebay.com"
        self.search_terms = ["Jordan 1", "Nike Dunk"]
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

    def build_search_url(self, search_term, limit=20):
        """Build eBay search URL"""
        # Replace spaces with +
        encoded_term = search_term.replace(' ', '+')

        # eBay search URL with filters for sneakers
        url = f"{self.base_url}/sch/i.html?_from=R40&_nkw={encoded_term}"
        url += "&_sacat=15709"  # Men's Shoes category
        url += "&_sop=10"  # Sort by newly listed
        url += "&_ipg=50"  # Items per page
        url += "&LH_Auction=1"  # Include auctions
        url += "&LH_BIN=1"  # Include Buy It Now
        url += "&_dcat=15709"  # Sneakers category

        return url

    async def fetch_page(self, session, url):
        """Fetch page content with error handling"""
        try:
            # Add random delay to avoid being blocked
            await asyncio.sleep(random.uniform(1, 3))

            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logger.warning(f"HTTP {response.status} for URL: {url}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def parse_price(self, price_text):
        """Extract price from text"""
        if not price_text:
            return 0.0

        # Remove currency symbols and extract number
        # Adjusted regex to handle cases like "$1,234.56" and "$12.00 to $20.00"
        price_match = re.search(r'(\d[\d.,]*)', price_text)
        if price_match:
            price_str = price_match.group(1).replace(',', '')
            try:
                return float(price_str)
            except ValueError:
                return 0.0
        return 0.0

    def parse_listings(self, html_content):
        """Parse eBay search results and extract upper material and condition"""
        soup = BeautifulSoup(html_content, 'html.parser')
        listings = []

        # Main container for each listing is now <li> with class 's-item'
        items = soup.find_all('li', class_='s-item')

        for item in items:
            try:
                # Skip sponsored items and ads
                # The 'SPONSORED' span is often inside the s-item__info div now
                if item.find('span', class_='s-item__hl-tag') and "SPONSORED" in item.find('span',
                                                                                           class_='s-item__hl-tag').get_text(
                        strip=True).upper():
                    continue

                # Check for "Shop on eBay" and similar titles from the primary link
                link_elem = item.find('a', class_='s-item__link')
                if not link_elem:
                    continue

                # Extract title from within the 's-item__title' div inside the link
                title_div_elem = link_elem.find('div', class_='s-item__title')
                if not title_div_elem:
                    continue

                # The actual title text is within a span with role="heading"
                title_span_elem = title_div_elem.find('span', {'role': 'heading', 'aria-level': '3'})
                if not title_span_elem:
                    continue

                title = title_span_elem.get_text(strip=True)

                if title.lower() in ['shop on ebay', 'new listing', 'newly listed', 'sponsored']:
                    continue

                url = link_elem.get('href')
                if not url:
                    continue

                # Clean URL (remove tracking parameters)
                url = url.split('?')[0] if '?' in url else url

                # Extract price from span with class 's-item__price'
                price_elem = item.find('span', class_='s-item__price')
                if not price_elem:
                    # Fallback for alternative price display if primary fails (e.g., "See price")
                    price_elem = item.find('span', class_='s-price-range')  # For price ranges
                    if not price_elem:
                        # Another common location for price
                        price_elem = item.find('div', class_='s-item__price')  # Sometimes it's a div
                        if not price_elem:
                            continue  # No price found, skip listing

                price_text = price_elem.get_text(strip=True)
                price = self.parse_price(price_text)

                if price <= 0:
                    continue

                # Extract condition from span with class 'SECONDARY_INFO' within 's-item__subtitle'
                condition_elem = item.find('div', class_='s-item__subtitle').find('span',
                                                                                  class_='SECONDARY_INFO') if item.find(
                    'div', class_='s-item__subtitle') else None
                condition = condition_elem.get_text(strip=True) if condition_elem else 'Unknown'

                # Extract image URL
                # The img tag is usually inside 's-item__image-wrapper' or directly within 's-item__image'
                img_elem = item.find('div', class_='s-item__image-wrapper').find('img') if item.find('div',
                                                                                                     class_='s-item__image-wrapper') else None
                if not img_elem:
                    img_elem = item.find('div', class_='s-item__image').find('img')  # Fallback

                image_url = img_elem.get('src') if img_elem else None

                # Clean image URL
                if image_url and image_url.startswith('//'):
                    image_url = 'https:' + image_url

                # Infer Upper Material from title (as before, direct extraction requires product page visit)
                upper_material = 'Unknown'
                title_lower = title.lower()
                if 'patent leather' in title_lower:
                    upper_material = 'Patent Leather'
                elif 'synthetic' in title_lower:
                    upper_material = 'Synthetic'
                elif 'mesh' in title_lower:
                    upper_material = 'Mesh'
                elif 'nubuck' in title_lower:
                    upper_material = 'Nubuck'
                elif 'fabric' in title_lower:
                    upper_material = 'Fabric'
                elif 'faux leather' in title_lower:
                    upper_material = 'Faux Leather'
                elif 'leather' in title_lower:
                    upper_material = 'Leather'

                listing = {
                    'title': title,
                    'price': price,
                    'condition': condition,
                    'upper_material': upper_material,
                    'url': url,
                    'image_url': image_url
                }

                listings.append(listing)

            except Exception as e:
                # Log the error and the problematic HTML snippet for better debugging
                logger.warning(f"Error parsing listing: {e}")
                # You might want to uncomment the line below for deeper debugging
                # logger.warning(f"Problematic item HTML: {item}")
                continue

        return listings

    async def scrape_search_term(self, session, search_term, limit=20):
        """Scrape listings for a specific search term"""
        url = self.build_search_url(search_term, limit)
        logger.info(f"Scraping: {search_term}")

        html_content = await self.fetch_page(session, url)
        if not html_content:
            return []

        listings = self.parse_listings(html_content)

        # Filter for relevant listings and limit results
        filtered_listings = []
        for listing in listings:
            title_lower = listing['title'].lower()

            # Basic relevance check
            if any(term.lower() in title_lower for term in ['jordan', 'nike', 'dunk', 'air']):
                filtered_listings.append(listing)

            if len(filtered_listings) >= limit:
                break

        logger.info(f"Found {len(filtered_listings)} relevant listings for '{search_term}'")
        return filtered_listings

    async def scrape_listings(self):
        """Main scraping function"""
        all_listings = []

        async with aiohttp.ClientSession() as session:
            # Scrape all search terms
            tasks = []
            for search_term in self.search_terms:
                tasks.append(self.scrape_search_term(session, search_term))

            # Wait for all scraping tasks to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Collect all listings
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Scraping task failed: {result}")
                elif isinstance(result, list):
                    all_listings.extend(result)

        # Remove duplicates based on URL
        seen_urls = set()
        unique_listings = []

        for listing in all_listings:
            if listing['url'] not in seen_urls:
                seen_urls.add(listing['url'])
                unique_listings.append(listing)

        logger.info(f"Scraped {len(unique_listings)} unique listings total")
        return unique_listings


# Test function
async def test_scraper():
    """Test the scraper"""
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    scraper = SneakerScraper()
    listings = await scraper.scrape_listings()

    print(f"\n--- Found {len(listings)} listings: ---")
    for i, listing in enumerate(listings[:10]):  # Show first 10
        print(f"\n{i + 1}. Title: {listing['title']}")
        print(f"   Price: ${listing['price']:.2f}")
        print(f"   Condition: {listing['condition']}")
        print(f"   Upper Material: {listing['upper_material']}")
        print(f"   URL: {listing['url']}")
        print(f"   Image URL: {listing['image_url']}")


if __name__ == "__main__":
    asyncio.run(test_scraper())
