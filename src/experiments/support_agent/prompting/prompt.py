from dataclasses import dataclass, field


@dataclass(frozen=True)
class Prompt:
    role: str = ""
    policy: str = ""
    instruction: str = ""
    task_input: str = ""
    context: str = ""
    tools: list[str] = field(default_factory=list)
    output_schema: str = ""
    output_constraints: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)

    def render(self) -> str:
        sections: list[tuple[str, str]] = []
        if self.role:
            sections.append(("Role", self.role))
        if self.policy:
            sections.append(("Policy", self.policy))
        if self.instruction:
            sections.append(("Instruction", self.instruction))
        if self.task_input:
            sections.append(("Task Input", self.task_input))
        if self.context:
            sections.append(("Context", self.context))
        if self.tools:
            sections.append(("Tools", self._render_list(self.tools)))
        if self.output_schema:
            sections.append(("Output Schema", self.output_schema))
        if self.output_constraints:
            sections.append(
                ("Output Constraints", self._render_list(self.output_constraints))
            )
        if self.examples:
            sections.append(("Examples", "\n".join(self.examples)))
        return "\n\n".join(
            f"[{title}]\n{content}" for title, content in sections
        )

    @staticmethod
    def _render_list(items: list[str]) -> str:
        return "\n".join(f"- {item}" for item in items)
