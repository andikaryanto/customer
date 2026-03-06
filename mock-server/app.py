from __future__ import annotations

import json
from pathlib import Path

from flask import Flask, abort, jsonify, request

app = Flask(__name__)
DATA_PATH = Path(__file__).parent / "data" / "customers.json"


def load_customers() -> list[dict]:
    with DATA_PATH.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise ValueError("customers.json must contain a list")
    return data


CUSTOMERS = load_customers()


@app.get("/api/health")
def health() -> tuple[dict, int]:
    return {"status": "ok"}, 200


@app.get("/api/customers")
def list_customers():
    page = request.args.get("page", default=1, type=int)
    limit = request.args.get("limit", default=10, type=int)

    if page < 1 or limit < 1:
        return jsonify({"error": "page and limit must be positive integers"}), 400

    start = (page - 1) * limit
    end = start + limit
    paginated_data = CUSTOMERS[start:end]

    return jsonify(
        {
            "data": paginated_data,
            "total": len(CUSTOMERS),
            "page": page,
            "limit": limit,
        }
    )


@app.get("/api/customers/<customer_id>")
def get_customer(customer_id: str):
    customer = next((item for item in CUSTOMERS if item["customer_id"] == customer_id), None)
    if customer is None:
        abort(404, description=f"Customer {customer_id} not found")
    return jsonify(customer)


@app.errorhandler(404)
def handle_not_found(error):
    return jsonify({"error": str(error)}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
