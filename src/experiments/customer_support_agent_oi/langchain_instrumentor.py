from openinference.instrumentation.langchain import LangChainInstrumentor


class OiLangChainInstrumentor:
    _instrumented = False

    def instrument(self, tracer_provider) -> None:
        if OiLangChainInstrumentor._instrumented:
            return

        LangChainInstrumentor().instrument(
            tracer_provider=tracer_provider
        )
        OiLangChainInstrumentor._instrumented = True
