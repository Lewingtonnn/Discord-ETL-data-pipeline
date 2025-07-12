#!/usr/bin/env python3
"""
Alternative entry point for the Sneaker Deal Sniper Bot
Includes setup validation and better error handling
"""

import sys
import os
import json
import logging
from bs4 import BeautifulSoup
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'discord', 'aiohttp', 'requests'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nPlease install dependencies with:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def validate_config():
    """Validate configuration file"""
    config_file = 'config.json'
    
    if not os.path.exists(config_file):
        print(f"⚠️  Config file '{config_file}' not found.")
        print("The bot will create a default config file on first run.")
        print("Make sure to edit it with your Discord token and channel ID.")
        return True
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Check required fields
        discord_config = config.get('discord', {})
        if not discord_config.get('token'):
            print("❌ Discord token not set in config.json")
            print("Please add your Discord bot token to config.json")
            return False
        
        if not discord_config.get('channel_id'):
            print("❌ Discord channel ID not set in config.json")
            print("Please add your Discord channel ID to config.json")
            return False
        
        print("✅ Configuration validated successfully")
        return True
        
    except json.JSONDecodeError:
        print("❌ Invalid JSON in config.json")
        print("Please check the config file format")
        return False
    except Exception as e:
        print(f"❌ Error reading config: {e}")
        return False

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('bot.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """Main function with setup validation"""
    print("🔥 Sneaker Deal Sniper Bot")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print("✅ Python version check passed")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    print("✅ Dependencies check passed")
    
    # Validate configuration
    #if not validate_config():
        #sys.exit(1)
    
    # Setup logging
    setup_logging()
    
    # Import and run bot
    try:
        print("🚀 Starting Sneaker Deal Sniper Bot...")
        print("Press Ctrl+C to stop the bot")
        print("=" * 50)
        
        from sneaker_bot import main as bot_main
        bot_main()
        
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all bot files are in the same directory")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()