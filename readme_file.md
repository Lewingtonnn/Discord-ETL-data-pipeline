# 🔥 Sneaker Deal Sniper Bot

A real-time eBay sneaker deal monitor that automatically posts filtered listings to Discord. Perfect for sneaker resellers looking to snipe underpriced deals on Jordan 1s and Nike Dunks.

## ✨ Features

- **Real-time Monitoring**: Checks eBay every 3 minutes for new listings
- **Smart Filtering**: Price range, keyword inclusion/exclusion filters
- **Deal Scoring**: Automatically rates deals from 1-10 based on price and keywords
- **Deduplication**: Never posts the same listing twice
- **Discord Integration**: Posts deals as rich embeds with images
- **Easy Configuration**: JSON-based config file
- **Logging**: Comprehensive logging for debugging and monitoring

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.8 or higher
- Discord bot token
- Discord server with a channel for deal alerts

### 2. Installation

```bash
# Clone or download the project files
git clone <repository-url>
cd sneaker-deal-bot

# Install dependencies
pip install -r requirements.txt
```

### 3. Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section and create a bot
4. Copy the bot token
5. Invite the bot to your server with these permissions:
   - Send Messages
   - Use Slash Commands
   - Embed Links
   - Read Message History

### 4. Configuration

The bot will create a `config.json` file on first run. Edit it with your settings:

```json
{
    "discord": {
        "token": "YOUR_BOT_TOKEN_HERE",
        "channel_id": "YOUR_CHANNEL_ID_HERE"
    },
    "scraping": {
        "search_terms": ["Jordan 1", "Nike Dunk"],
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
    }
}
```

### 5. Get Discord Channel ID

1. Enable Developer Mode in Discord (Settings > Advanced > Developer Mode)
2. Right-click on your channel and select "Copy ID"
3. Paste the ID into the config file

### 6. Run the Bot

```bash
python bot.py
```

## 📊 Deal Scoring System

The bot automatically calculates a deal score (1-10) based on:

- **Price Ranges**:
  - Under $60: Score 10 (🔥 Fire deal)
  - $60-80: Score 9 (Excellent)
  - $80-100: Score 8 (Very Good)
  - $100-120: Score 7 (Good)
  - $120-140: Score 6 (Fair)
  - $140-160: Score 5 (Average)
  - $160-180: Score 4 (Below Average)
  - $180-200: Score 3 (Poor)
  - $200+: Score 2 (Very Poor)

- **Bonus Points** (+1-2 points):
  - Popular models (Jordan 1, Dunk Low/High)
  - Retro releases
  - Hype collaborations (Off-White, Travis Scott, Fragment)

## 🎯 Filtering Options

### Search Terms
- Default: "Jordan 1" and "Nike Dunk"
- Customize in `config.json` under `scraping.search_terms`

### Price Filters
- Set minimum and maximum price ranges
- Default: $50 - $300

### Keyword Filters
- **Include Keywords**: Must contain at least one of these terms
- **Exclude Keywords**: Automatically filtered out if they contain these terms

### Examples of Filtered Content
- ✅ "Air Jordan 1 High Chicago 2015 Size 10 $85"
- ❌ "Jordan 1 Kids Size 5 $60" (contains "kids")
- ❌ "Jordan 1 Custom Paint $45" (contains "custom")
- ❌ "Jordan 1 Retro High $350" (exceeds max price)

## 🗂️ Project Structure

```
sneaker-deal-bot/
├── bot.py              # Main bot script
├── scraper.py          # eBay scraping logic
├── config.py           # Configuration management
├── config.json         # Bot configuration (auto-created)
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── sneaker_deals.db   # SQLite database (auto-created)
└── bot.log            # Log file (auto-created)
```

## 🔧 Configuration Details

### Discord Settings
```json
"discord": {
    "token": "YOUR_BOT_TOKEN",           # Discord bot token
    "channel_id": "123456789012345678"   # Channel ID for posting deals
}
```

### Scraping Settings
```json
"scraping": {
    "search_terms": ["Jordan 1", "Nike Dunk"],  # What to search for
    "check_interval_minutes": 3,                # How often to check
    "max_listings_per_search": 20               # Max results per search
}
```

### Filter Settings
```json
"filters": {
    "min_price": 50,                    # Minimum price
    "max_price": 300,                   # Maximum price
    "include_keywords": [...],          # Must contain these terms
    "exclude_keywords": [...]           # Cannot contain these terms
}
```

## 🚨 Important Notes

### Rate Limiting
- The bot includes built-in delays to avoid being blocked by eBay
- Checks every 3 minutes by default (configurable)
- Random delays between requests (1-3 seconds)

### Legal Considerations
- This bot is for educational purposes
- Respect eBay's robots.txt and terms of service
- Don't overload their servers with requests
- Use responsibly and ethically

### Database
- Uses SQLite for deduplication
- Automatically cleans up old listings (7 days)
- Stores listing URLs, titles, and prices

## 🐛 Troubleshooting

### Common Issues

1. **Bot not posting deals**
   - Check Discord token and channel ID
   - Verify bot has permissions in the channel
   - Check logs for error messages

2. **No listings found**
   - eBay might be blocking requests
   - Try increasing the check interval
   - Verify search terms are correct

3. **Bot crashes**
   - Check the `bot.log` file for errors
   - Ensure all dependencies are installed
   - Verify Python version (3.8+)

### Debug Commands

```bash
# Test the scraper independently
python scraper.py

# Validate configuration
python config.py

# Check logs
tail -f bot.log
```

## 📈 Monitoring & Logs

The bot creates detailed logs in `bot.log`:
- Startup and shutdown events
- Scraping results and timing
- Deal posting confirmations
- Error messages and warnings

Log format:
```
2024-01-15 10:30:45 - INFO - Found 15 listings
2024-01-15 10:30:46 - INFO - Posted new deal: Air Jordan 1 High Chicago - $89.99
```

## 🔄 Advanced Usage

### Custom Search Terms
Add more search terms to cast a wider net:
```json
"search_terms": [
    "Jordan 1", "Nike Dunk", "Air Jordan 1", 
    "SB Dunk", "Jordan 1 High", "Jordan 1 Low"
]
```

### Tighter Filters
For only the best deals:
```json
"filters": {
    "min_price": 40,
    "max_price": 150,
    "include_keywords": ["Jordan 1", "Dunk"],
    "exclude_keywords": [
        "kids", "youth", "replica", "custom", 
        "damaged", "used", "worn", "beat"
    ]
}
```

### Multiple Channels
Modify the code to post to different channels based on deal score:
- High score deals (8-10): #fire-deals
- Medium score deals (5-7): #good-deals
- Low score deals (1-4): #other-deals

## 🚀 Deployment

### Local Development
```bash
python bot.py
```

### VPS Deployment
```bash
# Using screen/tmux
screen -S sneaker-bot
python bot.py
# Ctrl+A, D to detach

# Using systemd (Linux)
sudo systemctl enable sneaker-bot.service
sudo systemctl start sneaker-bot.service
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "bot.py"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is for educational purposes only. Please respect eBay's terms of service and use responsibly.

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section
2. Review the logs in `bot.log`
3. Verify your configuration
4. Test individual components

---

**Happy deal hunting! 🔥👟**