# Household Bot

Telegram bot for managing household payments and expenses built with Python.

## Tech Stack

- **Framework**: aiogram 3.x (async Telegram Bot API)
- **Database**: PostgreSQL with asyncpg
- **Config**: pydantic-settings with python-dotenv
- **Deployment**: Docker & docker-compose

## Project Structure

```
├── app/
│   ├── handlers/      # Telegram command handlers (payments, donors, reports)
│   ├── middlewares/   # Bot middlewares (admin checks)
│   ├── utils/         # Helper utilities
│   ├── config.py      # Settings from .env
│   ├── db.py          # Database connection
│   └── main.py        # Bot entry point
├── docker-compose.yml
├── Dockerfile
├── init.sql           # Database schema
└── requirements.txt
```

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python -m app.main

# Run with Docker
docker-compose up --build
```

## Environment Variables

Copy `.env.example` to `.env` and configure:
- `BOT_TOKEN` - Telegram bot token from @BotFather
- `ADMIN_IDS` - Comma-separated Telegram user IDs for admin access
- `DB_*` - PostgreSQL connection settings

## Code Style

- Use async/await for all I/O operations
- Type hints required for function signatures
- Handler functions should be in appropriate files under `handlers/`
