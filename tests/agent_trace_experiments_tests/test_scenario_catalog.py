import pytest

from experiments.agent_trace_experiments.scenario_catalog import TraceExperimentScenarioCatalog


def test_scenario_catalog_lists_control_flow_scenarios():
    catalog = TraceExperimentScenarioCatalog()

    assert catalog.names() == (
        "combined_policy_retry_success",
        "fallback_handoff",
        "missing_order_fallback",
        "policy_decision_fallback",
        "policy_retrieval_failure_fallback",
        "response_retry_exhaustion_fallback",
        "shipping_order_success",
        "unsupported_fallback",
    )


def test_scenarios_declare_covered_tasks_and_branches():
    catalog = TraceExperimentScenarioCatalog()

    for scenario_name in catalog.names():
        scenario = catalog.get(scenario_name)

        assert scenario.covered_tasks
        assert scenario.covered_branches


def test_scenario_catalog_rejects_unknown_scenario():
    catalog = TraceExperimentScenarioCatalog()

    with pytest.raises(ValueError, match="Unknown trace experiment scenario"):
        catalog.get("unknown")
