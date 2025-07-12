import json
import os
import logging

logger = logging.getLogger(__name__)

class Config:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.load_config()
    
    def load_config(self):
        """Load configuration from JSON file"""
        # Default configuration
        default_config = {
            "discord": {
                "token": "",
                "channel_id": ""
            },
            "scraping": {
                "search_terms": ["Jordan 1", "Nike Dunk","Adidas"],
                "check_interval_minutes": 3,
                "max_listings_per_search": 20
            },
            "filters": {
                "min_price": 50,
                "max_price": 300,
                "include_keywords": [
                    "Jordan 1", "AJ1", "Air Jordan 1",
                    "Nike Dunk", "Dunk Low", "Dunk High", "SB Dunk"
                ],
                "exclude_keywords": [
                    "kids", "youth", "toddler", "infant", "baby",
                    "replica", "fake", "custom", "damaged", "broken",
                    "used", "worn", "beat", "beater"
                ]
            },
            "deal_scoring": {
                "price_thresholds": {
                    "excellent": 80,
                    "good": 120,
                    "fair": 160,
                    "poor": 200
                },
                "bonus_keywords": [
                    "retro", "og", "original", "deadstock", "ds",
                    "off white", "travis scott", "fragment", "chicago"
                ]
            }
        }
        
        # Create config file if it doesn't exist
        if not os.path.exists(self.config_file):
            self.create_default_config(default_config)
            logger.info(f"Created default config file: {self.config_file}")
        
        # Load configuration
        try:
            with open(self.config_file, 'r') as f:
                config_data = json.load(f)
            
            # Discord settings
            self.DISCORD_TOKEN = config_data.get('discord', {}).get('token', '')
            self.DISCORD_CHANNEL_ID = int(config_data.get('discord', {}).get('channel_id', '0'))
            
            # Scraping settings
            scraping_config = config_data.get('scraping', {})
            self.SEARCH_TERMS = scraping_config.get('search_terms', default_config['scraping']['search_terms'])
            self.CHECK_INTERVAL = scraping_config.get('check_interval_minutes', default_config['scraping']['check_interval_minutes'])
            self.MAX_LISTINGS_PER_SEARCH = scraping_config.get('max_listings_per_search', default_config['scraping']['max_listings_per_search'])
            
            # Filter settings
            filter_config = config_data.get('filters', {})
            self.MIN_PRICE = filter_config.get('min_price', default_config['filters']['min_price'])
            self.MAX_PRICE = filter_config.get('max_price', default_config['filters']['max_price'])
            self.INCLUDE_KEYWORDS = filter_config.get('include_keywords', default_config['filters']['include_keywords'])
            self.EXCLUDE_KEYWORDS = filter_config.get('exclude_keywords', default_config['filters']['exclude_keywords'])
            
            # Deal scoring settings
            scoring_config = config_data.get('deal_scoring', {})
            self.PRICE_THRESHOLDS = scoring_config.get('price_thresholds', default_config['deal_scoring']['price_thresholds'])
            self.BONUS_KEYWORDS = scoring_config.get('bonus_keywords', default_config['deal_scoring']['bonus_keywords'])
            
            logger.info("Configuration loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self.load_defaults(default_config)
    
    def create_default_config(self, default_config):
        """Create default configuration file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=4)
        except Exception as e:
            logger.error(f"Error creating config file: {e}")
    
    def load_defaults(self, default_config):
        """Load default configuration values"""
        self.DISCORD_TOKEN = ''
        self.DISCORD_CHANNEL_ID = 0
        self.SEARCH_TERMS = default_config['scraping']['search_terms']
        self.CHECK_INTERVAL = default_config['scraping']['check_interval_minutes']
        self.MAX_LISTINGS_PER_SEARCH = default_config['scraping']['max_listings_per_search']
        self.MIN_PRICE = default_config['filters']['min_price']
        self.MAX_PRICE = default_config['filters']['max_price']
        self.INCLUDE_KEYWORDS = default_config['filters']['include_keywords']
        self.EXCLUDE_KEYWORDS = default_config['filters']['exclude_keywords']
        self.PRICE_THRESHOLDS = default_config['deal_scoring']['price_thresholds']
        self.BONUS_KEYWORDS = default_config['deal_scoring']['bonus_keywords']
    
    def update_config(self, key, value):
        """Update a configuration value"""
        try:
            with open(self.config_file, 'r') as f:
                config_data = json.load(f)
            
            # Update the value using dot notation
            keys = key.split('.')
            current = config_data
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            current[keys[-1]] = value
            
            # Save updated config
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=4)
            
            logger.info(f"Updated config: {key} = {value}")
            
        except Exception as e:
            logger.error(f"Error updating config: {e}")
    
    def validate_config(self):
        """Validate configuration and return list of issues"""
        issues = []
        
        if not self.DISCORD_TOKEN:
            issues.append("Discord token is not set")
        
        if not self.DISCORD_CHANNEL_ID:
            issues.append("Discord channel ID is not set")
        
        if self.MIN_PRICE >= self.MAX_PRICE:
            issues.append("Min price must be less than max price")
        
        if self.MIN_PRICE < 0:
            issues.append("Min price cannot be negative")
        
        if not self.SEARCH_TERMS:
            issues.append("No search terms configured")
        
        if self.CHECK_INTERVAL < 1:
            issues.append("Check interval must be at least 1 minute")
        
        return issues
    
    def print_config(self):
        """Print current configuration (without sensitive data)"""
        print("\n=== Current Configuration ===")
        print(f"Discord Token: {'*' * 10 if self.DISCORD_TOKEN else 'NOT SET'}")
        print(f"Discord Channel ID: {self.DISCORD_CHANNEL_ID}")
        print(f"Search Terms: {self.SEARCH_TERMS}")
        print(f"Check Interval: {self.CHECK_INTERVAL} minutes")
        print(f"Price Range: ${self.MIN_PRICE} - ${self.MAX_PRICE}")
        print(f"Include Keywords: {self.INCLUDE_KEYWORDS}")
        print(f"Exclude Keywords: {self.EXCLUDE_KEYWORDS}")
        print("===============================\n")

# Test function
if __name__ == "__main__":
    config = Config()
    config.print_config()
    
    issues = config.validate_config()
    if issues:
        print("Configuration Issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("Configuration is valid!")