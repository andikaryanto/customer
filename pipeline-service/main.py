from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models.customer import Customer
from services.ingestion import fetch_all_customers, upsert_customers

app = FastAPI(title="Customer Pipeline Service")


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/ingest")
def ingest_customers(db: Session = Depends(get_db)) -> dict:
    try:
        customers = fetch_all_customers(limit=10)
        if not customers:
            return {"status": "success", "records_processed": 0}

        processed = upsert_customers(db, customers)
        return {"status": "success", "records_processed": processed}
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {exc}") from exc


@app.get("/api/customers")
def list_customers(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    offset = (page - 1) * limit

    total = db.query(Customer).count()
    rows = db.execute(select(Customer).offset(offset).limit(limit)).scalars().all()

    return {
        "data": [
            {
                "customer_id": row.customer_id,
                "first_name": row.first_name,
                "last_name": row.last_name,
                "email": row.email,
                "phone": row.phone,
                "address": row.address,
                "date_of_birth": row.date_of_birth,
                "account_balance": float(row.account_balance) if row.account_balance is not None else None,
                "created_at": row.created_at,
            }
            for row in rows
        ],
        "total": total,
        "page": page,
        "limit": limit,
    }


@app.get("/api/customers/{customer_id}")
def get_customer(customer_id: str, db: Session = Depends(get_db)) -> dict:
    row = db.get(Customer, customer_id)
    if row is None:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")

    return {
        "customer_id": row.customer_id,
        "first_name": row.first_name,
        "last_name": row.last_name,
        "email": row.email,
        "phone": row.phone,
        "address": row.address,
        "date_of_birth": row.date_of_birth,
        "account_balance": float(row.account_balance) if row.account_balance is not None else None,
        "created_at": row.created_at,
    }
