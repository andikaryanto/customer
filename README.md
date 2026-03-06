# Backend Developer Technical Assessment Solution

Flow: `Flask JSON -> FastAPI ingest -> PostgreSQL`

## Run

```bash
docker-compose up -d --build
```

## Database Migration (Alembic)

- `pipeline-service` uses Alembic migration.
- On container startup, it runs `alembic upgrade head` before starting FastAPI.
- Initial migration file: `pipeline-service/alembic/versions/0001_create_customers.py`.

## Test Endpoints

```bash
# Flask health
curl http://localhost:5000/api/health

# Flask paginated customers
curl "http://localhost:5000/api/customers?page=1&limit=5"

# Flask single customer
curl http://localhost:5000/api/customers/CUST-0001

# Trigger ingestion
curl -X POST http://localhost:8000/api/ingest

# FastAPI paginated customers from DB
curl "http://localhost:8000/api/customers?page=1&limit=5"

# FastAPI single customer
curl http://localhost:8000/api/customers/CUST-0001
```

## Notes

- Customer source data is loaded from `mock-server/data/customers.json` (25 records).
- Ingestion fetches all pages from Flask automatically.
- Upsert is implemented with PostgreSQL `ON CONFLICT` on `customer_id`.
