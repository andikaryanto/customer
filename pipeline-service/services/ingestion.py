from __future__ import annotations

import os
from datetime import date, datetime
from decimal import Decimal
from typing import Any

import requests
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from models.customer import Customer

MOCK_SERVER_URL = os.getenv("MOCK_SERVER_URL", "http://mock-server:5000")


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value)


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _normalize_customer(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "customer_id": str(item["customer_id"]),
        "first_name": item["first_name"],
        "last_name": item["last_name"],
        "email": item["email"],
        "phone": item.get("phone"),
        "address": item.get("address"),
        "date_of_birth": _parse_date(item.get("date_of_birth")),
        "account_balance": Decimal(str(item.get("account_balance", 0))),
        "created_at": _parse_datetime(item.get("created_at")),
    }


def fetch_all_customers(limit: int = 10) -> list[dict[str, Any]]:
    all_customers: list[dict[str, Any]] = []
    page = 1

    while True:
        response = requests.get(
            f"{MOCK_SERVER_URL}/api/customers",
            params={"page": page, "limit": limit},
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()

        batch = payload.get("data", [])
        if not batch:
            break

        all_customers.extend(batch)
        total = int(payload.get("total", 0))
        if len(all_customers) >= total:
            break

        page += 1

    return all_customers


def upsert_customers(db: Session, customers: list[dict[str, Any]]) -> int:
    if not customers:
        return 0

    normalized = [_normalize_customer(item) for item in customers]

    stmt = insert(Customer).values(normalized)
    update_columns = {
        column.name: getattr(stmt.excluded, column.name)
        for column in Customer.__table__.columns
        if column.name != "customer_id"
    }

    db.execute(stmt.on_conflict_do_update(index_elements=[Customer.customer_id], set_=update_columns))
    db.commit()
    return len(normalized)
