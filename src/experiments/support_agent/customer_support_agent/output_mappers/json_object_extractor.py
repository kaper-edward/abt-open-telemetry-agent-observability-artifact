class JsonObjectExtractor:
    def extract(self, text: str) -> str:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            lines = [
                line
                for line in cleaned.splitlines()
                if not line.strip().startswith("```")
            ]
            cleaned = "\n".join(lines).strip()

        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1 or end < start:
            raise ValueError("JSON object not found.")

        return cleaned[start : end + 1]


DEFAULT_JSON_OBJECT_EXTRACTOR = JsonObjectExtractor()
