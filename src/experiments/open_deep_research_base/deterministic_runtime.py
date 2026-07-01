from dataclasses import dataclass


@dataclass(frozen=True)
class ResearchScenario:
    name: str
    user_id: str
    session_id: str
    question: str
    planned_queries: tuple[str, ...]
    retrieved_documents: tuple[str, ...]
    compressed_summary: str
    final_report: str
