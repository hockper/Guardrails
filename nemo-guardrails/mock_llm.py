# mock_llm.py
from typing import Any, List, Optional
from langchain_core.language_models.llms import LLM
from langchain_core.callbacks.manager import (
    CallbackManagerForLLMRun,
    AsyncCallbackManagerForLLMRun,
)


class MockLLM(LLM):
    """
    Mock Model isolado para testes de latência de Input Check.
    Retorna uma string fixa para confirmar que o prompt passou pelo Guardrails.
    """
    
    @property
    def _llm_type(self) -> str:
        return "mock-model-v1"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        
        return "MENSAGEM NÃO BLOQUEADA [Mock Model]"

    async def _acall(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """
        Execução assíncrona obrigatória para o NeMo Guardrails.
        Como é um mock estático, podemos apenas retornar a string de forma assíncrona.
        """
        return "MENSAGEM NÃO BLOQUEADA [Mock Model]"
    