from experiments.support_agent.prompting import Prompt


def test_prompt_renders_only_populated_sections_in_stable_order():
    prompt = Prompt(
        role="Support agent",
        instruction="Answer the request.",
        task_input="Where is O1001?",
        tools=["lookup_order"],
        output_constraints=["Do not invent facts."],
    )

    assert prompt.render() == (
        "[Role]\nSupport agent\n\n"
        "[Instruction]\nAnswer the request.\n\n"
        "[Task Input]\nWhere is O1001?\n\n"
        "[Tools]\n- lookup_order\n\n"
        "[Output Constraints]\n- Do not invent facts."
    )
