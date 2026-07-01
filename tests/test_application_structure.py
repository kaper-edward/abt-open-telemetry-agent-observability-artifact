from pathlib import Path


def test_support_application_owns_cli_and_chat_loop():
    support_application_directory = Path("src/experiments/support_application")

    assert not Path("src/experiments/support_agent/application.py").exists()
    assert not Path("src/experiments/support_agent/applications").exists()
    assert not (Path("src") / "support_agent" / "__main__.py").exists()
    assert {
        "__main__.py",
        "chat_runner.py",
        "console_boundary.py",
    } <= {path.name for path in support_application_directory.iterdir()}
    assert not (support_application_directory / "observability_mode.py").exists()


def test_compatibility_domain_module_is_removed():
    assert not Path("src/experiments/support_agent/domain.py").exists()


def test_config_classes_are_split_by_responsibility():
    config_directory = Path("src/experiments/support_agent/config")

    assert {
        "common_config.py",
        "customer_support_agent_config.py",
    } <= {path.name for path in config_directory.iterdir()}
    assert not (config_directory / "telemetry_config.py").exists()
    assert not (config_directory / "evaluation_agent_config.py").exists()
    assert not (config_directory / "application_config.py").exists()


def test_models_and_scenarios_are_owned_by_their_feature_packages():
    root_data_models = Path("src/experiments/support_agent/data_models")
    agent_llm_outputs = Path("src/experiments/support_agent/customer_support_agent/llm_outputs")

    assert {
        "customer.py",
        "order.py",
        "policy_decision.py",
    } <= {path.name for path in root_data_models.iterdir()}
    assert {
        "intent_extraction.py",
        "support_response.py",
    } <= {path.name for path in agent_llm_outputs.iterdir()}

    assert not Path("src/experiments/support_agent/models").exists()
    assert not Path("src/experiments/support_agent/customer_support_agent/models").exists()
    assert not Path("src/experiments/support_agent/evaluation").exists()
    assert not Path("src/experiments/support_agent/evaluation/models").exists()
    assert not Path("src/experiments/support_agent/scenarios.py").exists()
    assert not Path("src/experiments/support_agent/evaluation/scenarios.py").exists()


def test_support_application_main_contains_only_boundary_delegation():
    source = Path("src/experiments/support_application/__main__.py").read_text(encoding="utf-8")

    assert not Path("src/experiments/support_application/cli.py").exists()
    assert "while True" not in source
    assert "uuid4" not in source
    assert ".close()" not in source
    assert "ServiceHealthChecker" not in source
    assert "evaluate" not in source
    assert "Application" + "Factory" not in source
    assert "observability" not in source


def test_support_agent_and_application_do_not_depend_on_observability_packages():
    roots = [Path("src/experiments/support_agent"), Path("src/experiments/support_application")]
    forbidden_terms = [
        "aof",
        "ABT",
        "openinference",
        "opentelemetry",
        "TelemetryConfig",
        "ObservabilityMode",
        "customer_support_agent_abt",
        "customer_support_agent_oi",
    ]

    for root in roots:
        for path in root.rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            source = path.read_text(encoding="utf-8")
            for term in forbidden_terms:
                assert term not in source, f"{term} found in {path}"
