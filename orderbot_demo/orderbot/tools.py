"""OrderBot's backend: a tiny fake order database and the two tools the agent can call."""

from datetime import datetime, timedelta

import mlflow

TODAY = datetime(2026, 9, 15)  # pinned so the demo behaves the same every rehearsal

STANDARD_WINDOW_DAYS = 30
PROMO_WINDOW_DAYS = 10  # store rule: flash-sale ("promo") purchases get a shorter window

ORDERS = {
    "A1001": {
        "item": "Wireless Mouse",
        "status": "delivered",
        "purchased_on": TODAY - timedelta(days=45),
        "delivered_on": TODAY - timedelta(days=40),
        "promo": False,
    },
    # The trap: a flash-sale purchase. Delivered 20 days ago, so it LOOKS eligible
    # under the standard 30-day policy -- but promo orders only get 10 days, and
    # that rule lives nowhere except check_refund_eligibility. An agent that never
    # calls the eligibility tool has no way to know this and will wrongly approve it.
    "A1002": {
        "item": "Bluetooth Speaker",
        "status": "delivered",
        "purchased_on": TODAY - timedelta(days=25),
        "delivered_on": TODAY - timedelta(days=20),
        "promo": True,
    },
    "A1003": {
        "item": "Desk Lamp",
        "status": "delivered",
        "purchased_on": TODAY - timedelta(days=5),
        "delivered_on": TODAY - timedelta(days=2),
        "promo": False,
    },
    "A1004": {
        "item": "Yoga Mat",
        "status": "shipped",
        "purchased_on": TODAY - timedelta(days=3),
        "delivered_on": None,
        "promo": False,
    },
    "A1005": {
        "item": "Espresso Machine",
        "status": "cancelled",
        "purchased_on": TODAY - timedelta(days=10),
        "delivered_on": None,
        "promo": False,
    },
}


def _fmt(d):
    return d.strftime("%Y-%m-%d") if d else None


@mlflow.trace(span_type="TOOL")
def lookup_order(order_id: str) -> dict:
    """Look up an order's item, status, purchase date, and delivery date.

    Deliberately does NOT expose the `promo` flag -- that pricing/eligibility
    detail belongs to check_refund_eligibility, not to general order lookup.
    """
    order = ORDERS.get(order_id)
    if order is None:
        return {"error": f"No order found with id {order_id}"}
    return {
        "order_id": order_id,
        "item": order["item"],
        "status": order["status"],
        "purchased_on": _fmt(order["purchased_on"]),
        "delivered_on": _fmt(order["delivered_on"]),
    }


@mlflow.trace(span_type="TOOL")
def check_refund_eligibility(order_id: str) -> dict:
    """Authoritative refund eligibility check.

    Policy: delivered + within 30 days of delivery -- except flash-sale ("promo")
    purchases, which only get a 10-day window. That exception is the whole point:
    it's a real business rule that only this tool knows about.
    """
    order = ORDERS.get(order_id)
    if order is None:
        return {"error": f"No order found with id {order_id}"}

    if order["status"] == "cancelled":
        return {"eligible": False, "reason": "Order was cancelled; there is nothing to refund."}

    if order["status"] != "delivered" or order["delivered_on"] is None:
        return {"eligible": False, "reason": "Order has not been delivered yet."}

    window = PROMO_WINDOW_DAYS if order["promo"] else STANDARD_WINDOW_DAYS
    days_since_delivery = (TODAY - order["delivered_on"]).days
    eligible = days_since_delivery <= window
    promo_note = " (flash-sale purchases get a shorter, 10-day window)" if order["promo"] else ""
    reason = (
        f"Delivered {days_since_delivery} days ago, which is "
        f"{'within' if eligible else 'beyond'} the {window}-day refund window{promo_note}."
    )
    return {"eligible": eligible, "reason": reason}


TOOL_SPECS = {
    "lookup_order": {
        "name": "lookup_order",
        "description": "Look up an order by ID. Returns item, status, purchase date, and delivery date.",
        "input_schema": {
            "type": "object",
            "properties": {"order_id": {"type": "string"}},
            "required": ["order_id"],
        },
    },
    "check_refund_eligibility": {
        "name": "check_refund_eligibility",
        "description": (
            "Authoritative check for whether an order qualifies for a refund under store "
            "policy. Always defer to this tool rather than computing eligibility yourself."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"order_id": {"type": "string"}},
            "required": ["order_id"],
        },
    },
}

TOOL_IMPLS = {
    "lookup_order": lookup_order,
    "check_refund_eligibility": check_refund_eligibility,
}
