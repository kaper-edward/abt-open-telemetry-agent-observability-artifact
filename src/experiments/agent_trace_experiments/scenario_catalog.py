from dataclasses import dataclass


@dataclass(frozen=True)
class TraceExperimentScenario:
    name: str
    customer_id: str
    message: str
    session_id: str
    gateway_outputs: tuple[str, ...]
    covered_tasks: tuple[str, ...]
    covered_branches: tuple[str, ...]
    store_behavior: str = "default"
    policy_behavior: str = "default"
    fallback_response_behavior: str = "default"


class TraceExperimentScenarioCatalog:
    def __init__(self):
        self._scenarios = {
            scenario.name: scenario
            for scenario in [
                # Covers tasks:
                # - classify_and_extract
                # - route_request
                # - order_lookup_branch
                # - policy_decision_branch
                # - response_generation_branch
                # - answer_evaluation_branch
                # - finalize_branch
                #
                # Covers branches:
                # - classify_and_extract -> route_request
                # - route_request -> order_lookup_branch
                # - order_lookup_branch -> policy_decision_branch
                # - policy_decision_branch -> response_generation_branch
                # - response_generation_branch -> answer_evaluation_branch
                # - answer_evaluation_branch -> finalize_branch
                TraceExperimentScenario(
                    name="shipping_order_success",
                    customer_id="C001",
                    message="Where is order O1001?",
                    session_id="S-shipping",
                    gateway_outputs=(
                        intent_output("shipping", "O1001"),
                        response_output("Order O1001 is shipped."),
                    ),
                    covered_tasks=(
                        "classify_and_extract",
                        "route_request",
                        "order_lookup_branch",
                        "policy_decision_branch",
                        "response_generation_branch",
                        "answer_evaluation_branch",
                        "finalize_branch",
                    ),
                    covered_branches=(
                        "classify_and_extract -> route_request",
                        "route_request -> order_lookup_branch",
                        "order_lookup_branch -> policy_decision_branch",
                        "policy_decision_branch -> response_generation_branch",
                        "response_generation_branch -> answer_evaluation_branch",
                        "answer_evaluation_branch -> finalize_branch",
                    ),
                ),
                # Covers tasks:
                # - classify_and_extract
                # - route_request
                # - order_lookup_branch
                # - policy_retrieval_branch
                # - policy_decision_branch
                # - response_generation_branch
                # - retry_response_generation_branch
                # - answer_evaluation_branch
                # - finalize_branch
                #
                # Covers branches:
                # - classify_and_extract -> route_request
                # - route_request -> order_lookup_branch
                # - order_lookup_branch -> policy_retrieval_branch
                # - policy_retrieval_branch -> policy_decision_branch
                # - policy_decision_branch -> response_generation_branch
                # - response_generation_branch -> retry_response_generation_branch
                # - retry_response_generation_branch -> answer_evaluation_branch
                # - answer_evaluation_branch -> finalize_branch
                TraceExperimentScenario(
                    name="combined_policy_retry_success",
                    customer_id="C002",
                    message="Cancel order O1003",
                    session_id="S-complex",
                    gateway_outputs=(
                        intent_output("cancellation", "O1003"),
                        response_output("Order O9999 can be cancelled."),
                        response_output("Order O1003 can be cancelled."),
                    ),
                    covered_tasks=(
                        "classify_and_extract",
                        "route_request",
                        "order_lookup_branch",
                        "policy_retrieval_branch",
                        "policy_decision_branch",
                        "response_generation_branch",
                        "retry_response_generation_branch",
                        "answer_evaluation_branch",
                        "finalize_branch",
                    ),
                    covered_branches=(
                        "classify_and_extract -> route_request",
                        "route_request -> order_lookup_branch",
                        "order_lookup_branch -> policy_retrieval_branch",
                        "policy_retrieval_branch -> policy_decision_branch",
                        "policy_decision_branch -> response_generation_branch",
                        "response_generation_branch -> retry_response_generation_branch",
                        "retry_response_generation_branch -> answer_evaluation_branch",
                        "answer_evaluation_branch -> finalize_branch",
                    ),
                ),
                # Covers tasks:
                # - classify_and_extract
                # - route_request
                # - order_lookup_branch
                # - fallback_response_branch
                # - finalize_branch
                #
                # Covers branches:
                # - classify_and_extract -> route_request
                # - route_request -> order_lookup_branch
                # - order_lookup_branch -> fallback_response_branch
                # - fallback_response_branch -> finalize_branch
                TraceExperimentScenario(
                    name="missing_order_fallback",
                    customer_id="C001",
                    message="Where is order O9999?",
                    session_id="S-missing-order",
                    gateway_outputs=(
                        intent_output("shipping", "O9999"),
                    ),
                    covered_tasks=(
                        "classify_and_extract",
                        "route_request",
                        "order_lookup_branch",
                        "fallback_response_branch",
                        "finalize_branch",
                    ),
                    covered_branches=(
                        "classify_and_extract -> route_request",
                        "route_request -> order_lookup_branch",
                        "order_lookup_branch -> fallback_response_branch",
                        "fallback_response_branch -> finalize_branch",
                    ),
                ),
                # Covers tasks:
                # - classify_and_extract
                # - route_request
                # - fallback_response_branch
                # - finalize_branch
                #
                # Covers branches:
                # - classify_and_extract -> route_request
                # - route_request -> fallback_response_branch
                # - fallback_response_branch -> finalize_branch
                TraceExperimentScenario(
                    name="unsupported_fallback",
                    customer_id="C001",
                    message="Can you recommend a movie?",
                    session_id="S-unsupported",
                    gateway_outputs=(
                        intent_output("unsupported", None),
                    ),
                    covered_tasks=(
                        "classify_and_extract",
                        "route_request",
                        "fallback_response_branch",
                        "finalize_branch",
                    ),
                    covered_branches=(
                        "classify_and_extract -> route_request",
                        "route_request -> fallback_response_branch",
                        "fallback_response_branch -> finalize_branch",
                    ),
                ),
                # Covers tasks:
                # - classify_and_extract
                # - route_request
                # - order_lookup_branch
                # - policy_decision_branch
                # - response_generation_branch
                # - retry_response_generation_branch
                # - fallback_response_branch
                # - finalize_branch
                #
                # Covers branches:
                # - classify_and_extract -> route_request
                # - route_request -> order_lookup_branch
                # - order_lookup_branch -> policy_decision_branch
                # - policy_decision_branch -> response_generation_branch
                # - response_generation_branch -> retry_response_generation_branch
                # - retry_response_generation_branch -> fallback_response_branch
                # - fallback_response_branch -> finalize_branch
                TraceExperimentScenario(
                    name="response_retry_exhaustion_fallback",
                    customer_id="C001",
                    message="Where is order O1001?",
                    session_id="S-retry-exhaustion",
                    gateway_outputs=(
                        intent_output("shipping", "O1001"),
                        response_output("Order O9999 is shipped."),
                        response_output("Order O9999 is shipped again."),
                    ),
                    covered_tasks=(
                        "classify_and_extract",
                        "route_request",
                        "order_lookup_branch",
                        "policy_decision_branch",
                        "response_generation_branch",
                        "retry_response_generation_branch",
                        "fallback_response_branch",
                        "finalize_branch",
                    ),
                    covered_branches=(
                        "classify_and_extract -> route_request",
                        "route_request -> order_lookup_branch",
                        "order_lookup_branch -> policy_decision_branch",
                        "policy_decision_branch -> response_generation_branch",
                        "response_generation_branch -> retry_response_generation_branch",
                        "retry_response_generation_branch -> fallback_response_branch",
                        "fallback_response_branch -> finalize_branch",
                    ),
                ),
                # Covers tasks:
                # - classify_and_extract
                # - route_request
                # - order_lookup_branch
                # - policy_retrieval_branch
                # - fallback_response_branch
                # - finalize_branch
                #
                # Covers branches:
                # - classify_and_extract -> route_request
                # - route_request -> order_lookup_branch
                # - order_lookup_branch -> policy_retrieval_branch
                # - policy_retrieval_branch -> fallback_response_branch
                # - fallback_response_branch -> finalize_branch
                TraceExperimentScenario(
                    name="policy_retrieval_failure_fallback",
                    customer_id="C002",
                    message="Cancel order O1003",
                    session_id="S-policy-retrieval-failure",
                    gateway_outputs=(
                        intent_output("cancellation", "O1003"),
                    ),
                    covered_tasks=(
                        "classify_and_extract",
                        "route_request",
                        "order_lookup_branch",
                        "policy_retrieval_branch",
                        "fallback_response_branch",
                        "finalize_branch",
                    ),
                    covered_branches=(
                        "classify_and_extract -> route_request",
                        "route_request -> order_lookup_branch",
                        "order_lookup_branch -> policy_retrieval_branch",
                        "policy_retrieval_branch -> fallback_response_branch",
                        "fallback_response_branch -> finalize_branch",
                    ),
                    store_behavior="policy_lookup_failure",
                ),
                # Covers tasks:
                # - classify_and_extract
                # - route_request
                # - order_lookup_branch
                # - policy_retrieval_branch
                # - policy_decision_branch
                # - fallback_response_branch
                # - finalize_branch
                #
                # Covers branches:
                # - classify_and_extract -> route_request
                # - route_request -> order_lookup_branch
                # - order_lookup_branch -> policy_retrieval_branch
                # - policy_retrieval_branch -> policy_decision_branch
                # - policy_decision_branch -> fallback_response_branch
                # - fallback_response_branch -> finalize_branch
                TraceExperimentScenario(
                    name="policy_decision_fallback",
                    customer_id="C002",
                    message="Cancel order O1003",
                    session_id="S-policy-decision-fallback",
                    gateway_outputs=(
                        intent_output("cancellation", "O1003"),
                    ),
                    covered_tasks=(
                        "classify_and_extract",
                        "route_request",
                        "order_lookup_branch",
                        "policy_retrieval_branch",
                        "policy_decision_branch",
                        "fallback_response_branch",
                        "finalize_branch",
                    ),
                    covered_branches=(
                        "classify_and_extract -> route_request",
                        "route_request -> order_lookup_branch",
                        "order_lookup_branch -> policy_retrieval_branch",
                        "policy_retrieval_branch -> policy_decision_branch",
                        "policy_decision_branch -> fallback_response_branch",
                        "fallback_response_branch -> finalize_branch",
                    ),
                    policy_behavior="needs_information",
                ),
                # Covers tasks:
                # - classify_and_extract
                # - route_request
                # - fallback_response_branch
                # - handoff_branch
                # - finalize_branch
                #
                # Covers branches:
                # - classify_and_extract -> route_request
                # - route_request -> fallback_response_branch
                # - fallback_response_branch -> handoff_branch
                # - handoff_branch -> finalize_branch
                TraceExperimentScenario(
                    name="fallback_handoff",
                    customer_id="C001",
                    message="Can you recommend a movie?",
                    session_id="S-fallback-handoff",
                    gateway_outputs=(
                        intent_output("unsupported", None),
                    ),
                    covered_tasks=(
                        "classify_and_extract",
                        "route_request",
                        "fallback_response_branch",
                        "handoff_branch",
                        "finalize_branch",
                    ),
                    covered_branches=(
                        "classify_and_extract -> route_request",
                        "route_request -> fallback_response_branch",
                        "fallback_response_branch -> handoff_branch",
                        "handoff_branch -> finalize_branch",
                    ),
                    fallback_response_behavior="empty",
                ),
            ]
        }

    def get(self, name: str) -> TraceExperimentScenario:
        try:
            return self._scenarios[name]
        except KeyError as error:
            raise ValueError(f"Unknown trace experiment scenario: {name}") from error

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._scenarios))


def intent_output(intent: str, order_id: str | None) -> str:
    order_json = "null" if order_id is None else f'"{order_id}"'
    return f'{{"intent":"{intent}","order_id":{order_json}}}'


def response_output(response: str) -> str:
    return f'{{"response":"{response}"}}'
