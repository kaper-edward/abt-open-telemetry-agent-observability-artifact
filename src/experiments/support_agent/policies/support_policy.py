from datetime import date

from experiments.support_agent.customer_support_agent.workspace import Intent
from experiments.support_agent.data_models import Order, PolicyDecision


class SupportPolicy:
    def decide(
        self,
        intent: Intent,
        order: Order | None,
        today: date,
    ) -> PolicyDecision:
        if order is None:
            return PolicyDecision(
                "needs_information", "order_required",
                "A valid owned order is required.",
            )

        if intent == "cancellation":
            if order.status in {"pending", "processing"}:
                return PolicyDecision(
                    "allowed", "not_shipped", "The order has not shipped."
                )
            if order.status == "cancelled":
                return PolicyDecision(
                    "denied", "already_shipped", "The order is already cancelled."
                )
            if order.status == "refunded":
                return PolicyDecision(
                    "denied", "already_shipped",
                    "The order has already been refunded.",
                )
            return PolicyDecision(
                "denied", "already_shipped",
                "Shipped orders cannot be cancelled.",
            )

        if intent == "return":
            if (
                order.status != "delivered"
                or order.delivered_on is None
                or order.delivered_on > today
            ):
                return PolicyDecision(
                    "denied", "not_delivered",
                    "Only delivered orders can be returned.",
                )
            if order.final_sale:
                return PolicyDecision(
                    "denied", "final_sale",
                    "Final-sale items cannot be returned.",
                )
            if (today - order.delivered_on).days > 30:
                return PolicyDecision(
                    "denied", "return_window_expired",
                    "The 30-day return window expired.",
                )
            if order.opened and not order.damaged:
                return PolicyDecision(
                    "denied", "opened_item",
                    "Opened non-defective items cannot be returned.",
                )
            return PolicyDecision(
                "allowed", "within_return_window",
                "The item is within the return window.",
            )

        if intent == "refund":
            if order.status not in {"cancelled", "refunded"}:
                return PolicyDecision(
                    "denied", "refund_not_started",
                    "No refund has been initiated.",
                )
            if order.refund_method not in {"original_payment", "store_credit"}:
                return PolicyDecision(
                    "denied", "unsupported_refund_method",
                    "The recorded refund method is not supported.",
                )
            return PolicyDecision(
                "allowed", f"refund_{order.refund_method}",
                "The refund follows the recorded method.",
            )

        return PolicyDecision(
            "not_applicable", "informational_request",
            "No policy decision is required.",
        )
