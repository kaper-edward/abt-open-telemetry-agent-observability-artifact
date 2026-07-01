def test_support_agent_package_is_importable():
    import experiments.support_agent as support_agent

    assert support_agent.__file__ is not None
