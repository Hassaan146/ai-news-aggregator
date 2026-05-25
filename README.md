# AI News Aggregator

AI News Aggregator is a full-stack AI news product that scrapes trusted AI
sources, stores articles and YouTube updates in PostgreSQL, generates digest
summaries with an LLM, ranks them against user priorities, and exposes the
result in a React dashboard.

Last updated: May 26, 2026

## What It Does

- Scrapes AI news, research, product blogs, newsletters, policy sources, and
  YouTube channel RSS feeds.
- Stores fetched URLs, titles, summaries, metadata, and transcripts/status in
  the database.
- Creates digest rows from stored news items.
- Ranks digest rows according to each user's selected sources, content types,
  and keywords.
- Falls back to deterministic ranking/summaries if the LLM is unavailable.
- Supports user accounts, reviews, Stripe checkout, and daily email delivery.

## Source Coverage

The scraper source registry lives in:

```text
app/scrapers/sources.py
```

Current website source count:

```text
164 website sources
```

The YouTube channel registry lives in:

```text
app/scrapers/youtube_channels.py
```

Current YouTube source count:

```text
36 AI YouTube channels
```

The source categories include:

- Official AI companies and labs
- AI developer platforms and agent frameworks
- Vector database and RAG tooling blogs
- AI news and tech media
- Research labs and paper-tracking sources
- Newsletters and curated feeds
- AI policy, safety, and security sources
- YouTube AI news, research, and builder channels

## Important Runtime Limits

The dashboard is intentionally capped so one user request does not overload the
scrapers or LLM key:

```text
Lookback window: up to 72 hours
Digest results: up to 10 articles
Default digest window: 72 hours
Default digest count: 10
```

Undated sources are handled as latest scraped posts. Dated posts are preferred
first; if fewer than 10 dated posts are available, latest undated posts can fill
the remaining slots.

## LLM Setup

The current recommended LLM provider is Groq using OpenAI OSS 120B:

```env
LLM_PROVIDER=groq
LLM_MODEL=openai/gpt-oss-120b
GROQ_API_KEY=your_groq_api_key
```

Gemini can still be used as fallback/manual replacement:

```env
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.5-flash-lite
GEMINI_API_KEY=your_gemini_api_key
```

Never commit API keys. Add them only to `.env` locally or Render environment
variables in deployment.

## Render Environment Variables

Use these for the backend deployment:

```env
DATABASE_URL=your_neon_postgres_url
CORS_ORIGINS=https://your-vercel-url.vercel.app
AUTH_SECRET_KEY=your_long_random_secret
ADMIN_EMAILS=your_admin_email@gmail.com

LLM_PROVIDER=groq
LLM_MODEL=openai/gpt-oss-120b
GROQ_API_KEY=your_groq_api_key

SCRAPE_ON_DIGEST=true
SCRAPE_MAX_SOURCES=20
SCRAPE_SOURCE_LIMIT=3
SCRAPE_YOUTUBE_LIMIT=1
YOUTUBE_CHANNEL_LIMIT=10

DIGEST_GENERATION_LIMIT=25
DIGEST_GENERATION_DELAY_SECONDS=8
DIGEST_ALLOW_FALLBACK=true

STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
STRIPE_CHECKOUT_MODE=subscription
STRIPE_PRICE_ID=
STRIPE_AMOUNT_CENTS=0
STRIPE_CURRENCY=usd
STRIPE_INTERVAL=month
STRIPE_PRODUCT_NAME=AI News Daily Email Plan
APP_BASE_URL=https://your-render-backend-url.onrender.com
```

For live email sending:

```env
GMAIL_ADDRESS=your_sender_gmail@gmail.com
GMAIL_APP_PASSWORD=your_gmail_app_password
```

## Local Development

Install dependencies:

```powershell
pip install -r requirements.txt
npm install
```

Run the backend:

```powershell
py -m uvicorn app.web:app --host 127.0.0.1 --port 8000 --reload
```

Run the frontend:

```powershell
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

## Database Setup

Create tables:

```powershell
py -m app.database.create_tables
```

The deployed backend also auto-creates required tables on startup unless:

```env
AUTO_CREATE_TABLES=false
```

## Pipeline Flow

When a user clicks **Make and rank digests**:

1. The frontend validates the request before calling the backend.
2. The backend reads saved/selected priorities.
3. Selected source names are mapped to scraper sources.
4. Source URLs and YouTube RSS feeds are fetched.
5. Fetched items are stored/upserted in the database by URL.
6. Missing digest rows are generated from stored database rows.
7. The aggregator ranks digest rows against the user's profile.
8. The dashboard shows up to 10 readable digest cards.

## Useful Commands

Run the main pipeline:

```powershell
py main.py --source-limit 3 --youtube-limit 1 --lookback-hours 72 --store
```

Generate missing digest rows:

```powershell
py -m app.digest_runner --limit 25 --lookback-hours 72 --delay-seconds 8
```

Get top ranked digests:

```powershell
py -m app.aggregator_runner --hours 72 --top-digests --top-n 10
```

Preview email:

```powershell
py -m app.email_runner --to your_user@gmail.com --hours 72 --top-n 10 --no-llm
```

Send email:

```powershell
py -m app.email_runner --to your_user@gmail.com --hours 72 --top-n 10 --send --no-llm
```

## Deployment

Backend:

- Render web service
- Start command:

```text
uvicorn app.web:app --host 0.0.0.0 --port $PORT
```

Frontend:

- Vercel
- Add:

```env
VITE_API_BASE_URL=https://your-render-backend-url.onrender.com
```

After backend changes, redeploy Render. After frontend changes, redeploy Vercel.
