import discord
from discord.ext import tasks
import asyncio
import json
import sqlite3
import logging
from datetime import datetime, timedelta
import re
from scraper_module import SneakerScraper
from config_module import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SneakerBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        
        self.config = Config()
        self.scraper = SneakerScraper()
        self.db_path = 'sneaker_deals.db'
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database for deduplication"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS listings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE,
                title TEXT,
                price REAL,
                posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
        logger.info("Database initialized")
    
    def is_duplicate(self, url):
        """Check if listing already exists in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM listings WHERE url = ?', (url,))
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    
    def save_listing(self, listing):
        """Save new listing to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO listings (url, title, price)
                VALUES (?, ?, ?)
            ''', (listing['url'], listing['title'], listing['price']))
            conn.commit()
            logger.info(f"Saved listing: {listing['title']}")
        except sqlite3.IntegrityError:
            logger.warning(f"Duplicate listing ignored: {listing['title']}")
        finally:
            conn.close()
    
    def cleanup_old_listings(self, days=7):
        """Remove old listings from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cutoff_date = datetime.now() - timedelta(days=days)
        cursor.execute('DELETE FROM listings WHERE posted_at < ?', (cutoff_date,))
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        if deleted > 0:
            logger.info(f"Cleaned up {deleted} old listings")
    
    def calculate_deal_score(self, price, title):
        """Calculate deal score based on price and keywords"""
        score = 0
        
        # Base score on price ranges
        if price < 60:
            score = 10
        elif price < 80:
            score = 9
        elif price < 100:
            score = 8
        elif price < 120:
            score = 7
        elif price < 140:
            score = 6
        elif price < 160:
            score = 5
        elif price < 180:
            score = 4
        elif price < 200:
            score = 3
        else:
            score = 2
        
        # Bonus points for popular models
        title_lower = title.lower()
        if any(keyword in title_lower for keyword in ['jordan 1', 'aj1', 'air jordan 1']):
            score += 1
        if any(keyword in title_lower for keyword in ['dunk low', 'dunk high', 'sb dunk']):
            score += 1
        if 'retro' in title_lower:
            score += 1
        if any(keyword in title_lower for keyword in ['off white', 'travis scott', 'fragment']):
            score += 2
        
        return min(score, 10)  # Cap at 10
    
    def filter_listing(self, listing):
        """Apply filters to determine if listing should be posted"""
        price = listing['price']
        title = listing['title'].lower()
        
        # Price range filter
        if price < self.config.MIN_PRICE or price > self.config.MAX_PRICE:
            return False, "Price out of range"
        
        # Include keywords filter
        if self.config.INCLUDE_KEYWORDS:
            if not any(keyword.lower() in title for keyword in self.config.INCLUDE_KEYWORDS):
                return False, "No include keywords found"
        
        # Exclude keywords filter
        if self.config.EXCLUDE_KEYWORDS:
            if any(keyword.lower() in title for keyword in self.config.EXCLUDE_KEYWORDS):
                return False, "Exclude keyword found"
        
        return True, "Passed all filters"
    
    def create_embed(self, listing):
        """Create Discord embed for listing"""
        should_post, reason = self.filter_listing(listing)
        if not should_post:
            return None
        
        deal_score = self.calculate_deal_score(listing['price'], listing['title'])
        
        # Create embed
        embed = discord.Embed(
            title=f"🔥 {listing['title']}",
            url=listing['url'],
            color=0x00ff00 if deal_score >= 8 else 0xffa500 if deal_score >= 6 else 0xff0000
        )
        
        embed.add_field(name="💰 Price", value=f"${listing['price']:.2f}", inline=True)
        embed.add_field(name="📦 Condition", value=listing['condition'], inline=True)
        embed.add_field(name="⭐ Deal Score", value=f"{deal_score}/10", inline=True)
        
        if listing['image_url']:
            embed.set_thumbnail(url=listing['image_url'])
        
        embed.set_footer(text=f"Found on eBay • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return embed
    
    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f'Bot logged in as {self.user}')
        self.monitor_listings.start()
        logger.info("Started monitoring task")
    
    @tasks.loop(minutes=3)  # Check every 3 minutes
    async def monitor_listings(self):
        """Main monitoring loop"""
        try:
            logger.info("Starting scrape cycle...")
            
            # Get channel
            channel = self.get_channel(self.config.DISCORD_CHANNEL_ID)
            if not channel:
                logger.error(f"Could not find channel with ID: {self.config.DISCORD_CHANNEL_ID}")
                return
            
            # Scrape listings
            listings = await self.scraper.scrape_listings()
            logger.info(f"Found {len(listings)} listings")
            
            new_listings = []
            for listing in listings:
                if not self.is_duplicate(listing['url']):
                    embed = self.create_embed(listing)
                    if embed:  # Only if it passes filters
                        new_listings.append(listing)
                        self.save_listing(listing)
                        
                        # Send to Discord
                        await channel.send(embed=embed)
                        logger.info(f"Posted new deal: {listing['title']} - ${listing['price']}")
                        
                        # Small delay to avoid rate limits
                        await asyncio.sleep(1)
            
            if new_listings:
                logger.info(f"Posted {len(new_listings)} new deals")
            else:
                logger.info("No new deals found")
            
            # Cleanup old listings every 10 cycles
            if hasattr(self, '_cleanup_counter'):
                self._cleanup_counter += 1
            else:
                self._cleanup_counter = 1
                
            if self._cleanup_counter >= 10:
                self.cleanup_old_listings()
                self._cleanup_counter = 0
                
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
            await asyncio.sleep(60)  # Wait before retrying
    
    @monitor_listings.before_loop
    async def before_monitor_listings(self):
        """Wait until bot is ready before starting loop"""
        await self.wait_until_ready()

def main():
    """Main function to run the bot"""
    config = Config()
    
    if not config.DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN not found in config. Please set it in config.json")
        return
    
    if not config.DISCORD_CHANNEL_ID:
        logger.error("DISCORD_CHANNEL_ID not found in config. Please set it in config.json")
        return
    
    bot = SneakerBot()
    
    try:
        logger.info("Starting Sneaker Deal Sniper Bot...")
        bot.run(config.DISCORD_TOKEN)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")

if __name__ == "__main__":
    main()