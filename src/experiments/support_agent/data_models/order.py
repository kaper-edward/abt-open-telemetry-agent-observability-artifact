from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Order:
    id: str
    customer_id: str
    status: str
    product: str
    ordered_on: date
    delivered_on: date | None
    expected_delivery: date | None
    amount: float
    final_sale: bool = False
    opened: bool = False
    damaged: bool = False
    refund_method: str = "original_payment"
