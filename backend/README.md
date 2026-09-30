# SourceLens Backend

A complete FastAPI backend for a SaaS product sourcing platform. Users upload a photo of a product and the platform finds the cheapest, most trusted suppliers filtered by country using AI-powered image analysis and vector similarity search.

## Features

- **Authentication**: JWT-based auth with bcrypt password hashing
- **Image Upload**: Cloudinary integration with automatic expiration (30 days)
- **AI Analysis**: GPT-4o Vision for product category and attribute detection
- **Supplier Matching**: pgvector similarity search with composite scoring
- **Rate Limiting**: Plan-based limits (Free: 5/month, Pro/Business: unlimited)
- **Async Processing**: Celery workers for image analysis
- **Database**: PostgreSQL with pgvector extension
- **Caching**: Upstash Redis for Celery task queue

## Project Structure
You are a senior Python backend engineer. Build a complete FastAPI backend for a SaaS product sourcing platform called SourceLens. Users upload a photo of a product and the platform finds the cheapest, most trusted suppliers filtered by country.

=== PROJECT SETUP ===
Create a Python project with this structure:
  sourcelens-backend/
    app/
      main.py           (FastAPI app entry point)
      config.py         (env vars with pydantic-settings)
      database.py       (SQLAlchemy engine + session)
      models/           (SQLAlchemy models)
      schemas/          (Pydantic request/response schemas)
      routers/          (API route files)
      services/         (business logic)
      workers/          (Celery tasks)
    alembic/            (database migrations)
    requirements.txt
    Dockerfile
    docker-compose.yml
    .env.example

=== DATABASE MODELS ===
Create these SQLAlchemy models:

1. User
   - id (UUID, primary key)
   - email (unique, indexed)
   - hashed_password
   - plan (enum: free, pro, business, enterprise)
   - searches_this_month (int, default 0)
   - created_at (timestamp)

2. Supplier
   - id (UUID, primary key)
   - name (string)
   - country_code (ISO 3166-1 alpha-2, indexed)
   - categories (array of strings)
   - min_order_qty (int)
   - price_usd_per_unit (decimal)
   - trust_score (float 0-10)
   - verified (boolean)
   - website_url (string)
   - contact_email (string)
   - description (text)
   - embedding (vector(1536)) -- pgvector
   - created_at, updated_at

3. Search
   - id (UUID, primary key)
   - user_id (FK -> User)
   - image_s3_key (string)
   - image_expires_at (timestamp, 30 days from upload)
   - detected_category (string)
   - detected_attributes (JSONB)
   - confidence_score (float)
   - filters_applied (JSONB -- country, budget, MOQ)
   - result_supplier_ids (array of UUIDs)
   - created_at

4. SavedSupplier
   - id (UUID, primary key)
   - user_id (FK -> User)
   - supplier_id (FK -> Supplier)
   - notes (text)
   - created_at

=== API ENDPOINTS ===
Build these endpoints:

AUTH ROUTER (/api/auth)
  POST /register     -- create account, return JWT
  POST /login        -- email+password, return JWT
  GET  /me           -- return current user profile

UPLOAD ROUTER (/api/upload)
  POST /image        -- multipart form with 'image' field
    1. Authenticate user (JWT required)
    2. Check rate limit based on plan (free=5/month, pro=unlimited)
    3. Validate: max 10MB, types jpeg/png/webp only
    4. Upload original to Cloudinary with folder: sourcelens/{user_id}
    5. Set image_expires_at = now + 30 days
    6. Push Celery task: analyze_image(search_id, cloudinary_public_id)
    7. Return: { search_id, status: 'processing' }

  GET /status/{search_id}   -- poll for analysis result
    Return: { status: processing|complete|failed, result? }

SEARCH ROUTER (/api/search)
  GET  /results/{search_id}   -- get full supplier results
    Query params: country (ISO code), min_trust (float), max_price (float), limit (int)
    Return paginated supplier list sorted by composite score

  GET  /history               -- user's past searches (last 50)
  GET  /suppliers/{id}        -- full supplier detail page
  POST /save/{supplier_id}    -- save supplier to user watchlist
  GET  /saved                 -- list saved suppliers

=== AI ANALYSIS WORKER ===
Create a Celery task analyze_image(search_id, cloudinary_public_id):

Step 1 — Get Cloudinary image URL
Step 2 — Call GPT-4o Vision with this exact prompt:
  'Analyze this product image and return ONLY valid JSON with these fields:
   category (string), subcategory (string), material (string),
   color (string), estimated_size (string), style (string),
   keywords (array of 5-8 strings), confidence (float 0-1).
   No explanation, only JSON.'
Step 3 — If confidence < 0.70, set status='needs_clarification', stop
Step 4 — Generate text embedding: combine category + keywords into one string,
          call OpenAI text-embedding-3-small, store 1536-dim vector in Search.embedding
Step 5 — Run supplier matching (see below)
Step 6 — Update Search record with results, set status='complete'

=== SUPPLIER MATCHING ENGINE ===
Create service match_suppliers(search_id, filters):

Step 1 — pgvector similarity search:
  SELECT suppliers.*, 1 - (embedding <=> query_vector) AS similarity
  FROM suppliers
  WHERE country_code = ANY(filter_countries)  -- if filter set
  ORDER BY similarity DESC LIMIT 50

Step 2 — Re-rank by composite score:
  score = (similarity * 0.35) + (trust_score/10 * 0.40)
        + (price_fit * 0.15) + (moq_fit * 0.10)
  price_fit = 1 - min(price/max_budget, 1) if max_budget set, else 0.5
  moq_fit = 1 if min_order_qty <= user_moq else 0.3

Step 3 — Return top 20 suppliers with all fields

=== AUTHENTICATION & RATE LIMITING ===
- Use python-jose for JWT (HS256, 7-day expiry)
- Hash passwords with bcrypt
- Rate limit middleware: check User.searches_this_month
  Free plan: 5/month, Pro: unlimited, Business: unlimited + API key support
- Reset searches_this_month on the 1st of each month (Celery beat task)

=== ENVIRONMENT VARIABLES ===
Create .env.example with:
  DATABASE_URL, REDIS_URL, SECRET_KEY,
  CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET,
  OPENAI_API_KEY, FRONTEND_URL (for CORS)

=== CORS & SECURITY ===
- Allow origins from FRONTEND_URL env var
- Add trusted host middleware
- Rate limit all routes: 100 req/min per IP (use slowapi)

=== DOCKER SETUP ===
docker-compose.yml must start: FastAPI app, PostgreSQL, Celery worker.
Include a seed script that inserts 50 sample suppliers across 10 countries.
Note: Upstash Redis is used as a managed service, not included in docker-compose.

=== REQUIREMENTS ===
requirements.txt must include:
fastapi, uvicorn, sqlalchemy, alembic, psycopg2-binary, pgvector,
celery, redis, cloudinary, upstash-redis, openai, python-jose, passlib[bcrypt],
pydantic-settings, python-multipart, slowapi

Make all code production-ready with proper error handling, logging, and docstrings.
Every endpoint must return consistent JSON: { success, data?, error? }

Environment setup commands
# 1. Clone / create your project folder
mkdir sourcelens-backend && cd sourcelens-backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install fastapi uvicorn sqlalchemy alembic psycopg2-binary \
  pgvector celery redis boto3 openai python-jose passlib[bcrypt] \
  pydantic-settings python-multipart slowapi

# 4. Start services with Docker
docker-compose up -d

# 5. Run migrations
alembic upgrade head

# 6. Start the server
uvicorn app.main:app --reload --port 8000

# Test it:
curl http://localhost:8000/api/health

```
sourcelens-backend/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Environment variables with pydantic-settings
│   ├── database.py          # SQLAlchemy engine + session
│   ├── auth.py              # JWT & password hashing utilities
│   ├── models/              # SQLAlchemy models
│   │   ├── user.py
│   │   ├── supplier.py
│   │   ├── search.py
│   │   └── saved_supplier.py
│   ├── schemas/             # Pydantic request/response schemas
│   │   ├── common.py
│   │   ├── user.py
│   │   ├── supplier.py
│   │   ├── search.py
│   │   └── saved_supplier.py
│   ├── routers/             # API route files
│   │   ├── auth.py
│   │   ├── upload.py
│   │   └── search.py
│   ├── services/            # Business logic
│   │   └── matching.py      # Supplier matching with pgvector
│   └── workers/             # Celery tasks
│       └── celery_app.py    # Image analysis worker
├── alembic/                 # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 001_initial_schema.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── seed_suppliers.py        # Seed data script

## Environment Setup

### Option 1: Docker Setup

**Step 1: Install Docker Desktop**
- Download from https://www.docker.com/products/docker-desktop
- Install and start Docker Desktop
- Wait for Docker Desktop to be running

**Step 2: Configure Environment Variables**

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Required variables:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Upstash Redis connection string
- `SECRET_KEY` - JWT signing key (min 32 chars)
- `CLOUDINARY_CLOUD_NAME` - Cloudinary cloud name
- `CLOUDINARY_API_KEY` - Cloudinary API key
- `CLOUDINARY_API_SECRET` - Cloudinary API secret
- `OPENAI_API_KEY` - OpenAI API key for GPT-4o Vision
- `FRONTEND_URL` - Frontend URL for CORS

**Step 3: Start services with Docker**

```bash
docker-compose up -d
```

This starts:
- PostgreSQL with pgvector
- FastAPI application
- Celery worker
- Celery beat scheduler

Note: Upstash Redis is a managed service (set REDIS_URL in .env)

**Step 4: Wait for services to be healthy**
```bash
docker-compose ps
```

Wait until all services show "healthy" status (may take 30-60 seconds)

**Step 5: Run migrations**
```bash
docker-compose exec api alembic upgrade head
```

**Step 6: Seed database with sample suppliers**
```bash
docker-compose exec api python seed_suppliers.py
```

**Step 7: Verify the API is running**
```bash
curl http://localhost:8000/api/health
```

### Option 2: Local Development Setup

**Step 1: Install Python 3.11+**
Download from https://www.python.org/downloads/

**Step 2: Create Virtual Environment**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# OR
source venv/bin/activate  # Linux/Mac
```

**Step 3: Install Dependencies**
```bash
pip install -r requirements.txt
```

**Step 4: Install PostgreSQL with pgvector**
- Download PostgreSQL 16 from https://www.postgresql.org/download/
- Install pgvector extension:
  ```bash
  # On Windows with pgAdmin, run this SQL:
  CREATE EXTENSION IF NOT EXISTS vector;
  ```

**Step 5: Set Up Upstash Redis**
- Create a free account at https://upstash.com
- Create a Redis database
- Copy the Redis URL (REDIS_URL) to your .env file

**Step 6: Configure Environment Variables**
Same as Step 2 in Docker setup

**Step 7: Run Migrations**
```bash
alembic upgrade head
```

**Step 8: Seed Sample Suppliers**
```bash
python seed_suppliers.py
```

**Step 9: Start Celery Worker (in separate terminal)**
```bash
celery -A app.workers.celery_app worker --loglevel=info
```

**Step 10: Start Celery Beat (in another separate terminal)**
```bash
celery -A app.workers.celery_app beat --loglevel=info
```

**Step 11: Start the FastAPI Server**
```bash
uvicorn app.main:app --reload --port 8000
```

## API Endpoints

### Authentication (`/api/auth`)

- `POST /api/auth/register` - Create account, return JWT
- `POST /api/auth/login` - Email+password, return JWT
- `GET /api/auth/me` - Return current user profile

### Upload (`/api/upload`)

- `POST /api/upload/image` - Upload product image for analysis
  - Requires JWT authentication
  - Validates: max 10MB, types jpeg/png/webp only
  - Checks rate limit based on plan
  - Returns: `{ search_id, status: 'processing' }`
- `GET /api/upload/status/{search_id}` - Poll for analysis result
  - Returns: `{ status: processing|complete|failed, result? }`

### Search (`/api/search`)

- `GET /api/search/results/{search_id}` - Get full supplier results
  - Query params: `country`, `min_trust`, `max_price`, `limit`
  - Returns paginated supplier list sorted by composite score
- `GET /api/search/history` - User's past searches (last 50)
- `GET /api/search/suppliers/{id}` - Full supplier detail page
- `POST /api/search/save/{supplier_id}` - Save supplier to watchlist
- `GET /api/search/saved` - List saved suppliers

### Health Check

- `GET /api/health` - Service health check

## Database Models

### User
- `id` (UUID, primary key)
- `email` (unique, indexed)
- `hashed_password`
- `plan` (enum: free, pro, business, enterprise)
- `searches_this_month` (int, default 0)
- `created_at` (timestamp)

### Supplier
- `id` (UUID, primary key)
- `name` (string)
- `country_code` (ISO 3166-1 alpha-2, indexed)
- `categories` (array of strings)
- `min_order_qty` (int)
- `price_usd_per_unit` (decimal)
- `trust_score` (float 0-10)
- `verified` (boolean)
- `website_url` (string)
- `contact_email` (string)
- `description` (text)
- `embedding` (vector(1536)) -- pgvector
- `created_at`, `updated_at`

### Search
- `id` (UUID, primary key)
- `user_id` (FK -> User)
- `image_s3_key` (string) - Cloudinary public ID
- `image_expires_at` (timestamp, 30 days from upload)
- `detected_category` (string)
- `detected_attributes` (JSONB)
- `confidence_score` (float)
- `filters_applied` (JSONB -- country, budget, MOQ)
- `result_supplier_ids` (array of UUIDs)
- `created_at`

### SavedSupplier
- `id` (UUID, primary key)
- `user_id` (FK -> User)
- `supplier_id` (FK -> Supplier)
- `notes` (text)
- `created_at`

## AI Analysis Workflow

The Celery worker `analyze_image_task` performs the following steps:

1. **Get Cloudinary image URL**
2. **Call GPT-4o Vision** with prompt:
   ```
   Analyze this product image and return ONLY valid JSON with these fields:
   category (string), subcategory (string), material (string),
   color (string), estimated_size (string), style (string),
   keywords (array of 5-8 strings), confidence (float 0-1).
   No explanation, only JSON.
   ```
3. **Check confidence threshold** - If confidence < 0.70, set status='needs_clarification'
4. **Generate text embedding** - Combine category + keywords, call OpenAI text-embedding-3-small
5. **Run supplier matching** - Using pgvector similarity search
6. **Update Search record** with results, set status='complete'

## Supplier Matching Engine

The `match_suppliers` service uses a two-step approach:

### Step 1: pgvector Similarity Search
```sql
SELECT suppliers.*, 1 - (embedding <=> query_vector) AS similarity
FROM suppliers
WHERE country_code = ANY(filter_countries)
ORDER BY similarity DESC LIMIT 50
```

### Step 2: Composite Score Re-ranking
```
score = (similarity * 0.35) + (trust_score/10 * 0.40)
      + (price_fit * 0.15) + (moq_fit * 0.10)

price_fit = 1 - min(price/max_budget, 1) if max_budget set, else 0.5
moq_fit = 1 if min_order_qty <= user_moq else 0.3
```

Returns top 20 suppliers with all fields.

## Rate Limiting

- **Free plan**: 5 searches per month
- **Pro plan**: Unlimited searches
- **Business/Enterprise**: Unlimited + API key support
- **Global rate limit**: 100 requests per minute per IP

Monthly search counters reset automatically on the 1st of each month via Celery beat.

## Security

- JWT tokens with 7-day expiry
- Bcrypt password hashing
- CORS configured for frontend URL
- Trusted host middleware
- Rate limiting on all routes
- Cloudinary URLs with auto-optimization

## Testing

Test the health endpoint:
```bash
curl http://localhost:8000/api/health
```

Test registration:
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","plan":"free"}'
```

## Development

### Create new migrations
```bash
alembic revision --autogenerate -m "description"
```

### Apply migrations
```bash
alembic upgrade head
```

### Rollback migrations
```bash
alembic downgrade -1
```

### View logs
```bash
docker-compose logs -f api
docker-compose logs -f celery-worker
```

## Production Considerations

1. **Environment Variables**: Never commit `.env` file
2. **SECRET_KEY**: Use a strong, randomly generated key
3. **Database**: Use managed PostgreSQL service
4. **S3**: Configure bucket policies and CORS
5. **Monitoring**: Add application monitoring (e.g., Sentry)
6. **Logging**: Configure centralized logging
7. **HTTPS**: Use reverse proxy (nginx) with SSL
8. **Scaling**: Use multiple Celery workers for high load

## License

MIT License
