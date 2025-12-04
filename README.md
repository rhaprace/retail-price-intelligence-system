# Retail Price Intelligence System

Track and compare product prices across e-commerce platforms.

## Quick Start

```bash
cp env.example .env
# Set DB_PASSWORD and JWT_SECRET_KEY in .env

docker-compose up -d
```

**API:** http://localhost:8000/docs  
**Frontend:** http://localhost:5173

## Local Development

```bash
# Backend
cd server
pip install -r requirements.txt
python run_api.py

# Frontend
cd client
npm install
npm run dev
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DB_PASSWORD` | Yes | PostgreSQL password |
| `JWT_SECRET_KEY` | Yes | Auth secret (`openssl rand -hex 32`) |
| `DB_HOST` | No | Database host (default: localhost) |

## Testing

```bash
cd server && python -m pytest tests/ -v
```

## Tech Stack

**Backend:** FastAPI, SQLAlchemy, PostgreSQL, Redis  
**Frontend:** React, TypeScript, Vite, TailwindCSS

## License

MIT
