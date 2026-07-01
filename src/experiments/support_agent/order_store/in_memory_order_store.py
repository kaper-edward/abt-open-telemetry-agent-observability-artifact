from dataclasses import dataclass
from datetime import date
from types import MappingProxyType
from typing import Mapping

from experiments.support_agent.customer_support_agent.workspace import Intent
from experiments.support_agent.data_models import Customer, Order


_POLICIES: Mapping[str, str] = MappingProxyType(
    {
        "order_status": (
            "Order status information is available only after the customer and "
            "order ownership are verified."
        ),
        "shipping": (
            "Shipping estimates use the order's expected delivery date and may "
            "change after the carrier accepts the package."
        ),
        "cancellation": (
            "Cancellation is allowed while an order is pending or processing, "
            "but not after it has shipped."
        ),
        "return": (
            "Return requests are accepted within 30 days of delivery unless the "
            "item is final sale or otherwise ineligible."
        ),
        "refund": (
            "Refund timing and destination follow the order's recorded refund "
            "method after the return is approved."
        ),
    }
)

_UNSUPPORTED_POLICY = (
    "I can't provide a policy for that request. Please ask about customer support "
    "topics such as orders, shipping, cancellations, returns, or refunds."
)


@dataclass(frozen=True)
class InMemoryOrderStore:
    """Demo data store for local agent execution and evaluation.

    This is not intended to represent a production database. It keeps fixture
    customers, orders, and support policies in memory so the example agent can
    run locally and be evaluated without external services. A real deployment
    could replace this class with a database-backed store, REST API-backed
    store, MCP tool-backed store, or repository/gateway wrapper.
    """

    customers: Mapping[str, Customer]
    orders: Mapping[str, Order]

    @classmethod
    def default(cls) -> "InMemoryOrderStore":
        customers = {
            "C001": Customer("C001", "Alex Morgan"),
            "C002": Customer("C002", "Blair Chen"),
            "C003": Customer("C003", "Casey Patel"),
            "C004": Customer("C004", "Drew Rivera"),
        }
        orders = {
            "O1001": Order(
                "O1001", "C001", "shipped", "Wireless Headphones",
                date(2026, 6, 7), None, date(2026, 6, 14), 129.99,
            ),
            "O1002": Order(
                "O1002", "C001", "delivered", "Travel Backpack",
                date(2026, 5, 8), date(2026, 5, 14),
                date(2026, 5, 15), 84.50, opened=True,
            ),
            "O1003": Order(
                "O1003", "C002", "pending", "Desk Lamp",
                date(2026, 6, 12), None, date(2026, 6, 18), 42.00,
            ),
            "O1004": Order(
                "O1004", "C002", "processing", "Linen Shirt",
                date(2026, 6, 10), None, date(2026, 6, 17), 58.25,
                final_sale=True,
            ),
            "O1005": Order(
                "O1005", "C003", "delivered", "Ceramic Cookware Set",
                date(2026, 4, 30), date(2026, 5, 12),
                date(2026, 5, 10), 210.00, damaged=True,
            ),
            "O1006": Order(
                "O1006", "C003", "cancelled", "Running Shoes",
                date(2026, 6, 2), None, None, 96.00,
            ),
            "O1007": Order(
                "O1007", "C004", "refunded", "Smart Watch Band",
                date(2026, 5, 1), date(2026, 5, 6),
                date(2026, 5, 7), 34.99, refund_method="store_credit",
            ),
            "O1008": Order(
                "O1008", "C004", "delivered", "Cotton Throw Blanket",
                date(2026, 5, 20), date(2026, 5, 27),
                date(2026, 5, 28), 72.00,
            ),
        }
        return cls(
            customers=MappingProxyType(customers),
            orders=MappingProxyType(orders),
        )

    def get_order(self, customer_id: str, order_id: str) -> Order | None:
        order = self.orders.get(order_id)
        if order is None or order.customer_id != customer_id:
            return None
        return order

    def get_policy(self, intent: Intent | str) -> str:
        return _POLICIES.get(intent, _UNSUPPORTED_POLICY)
