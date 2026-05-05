import asyncio
from typing import Any, List, Optional
from transformers import pipeline
# Usamos a classe base LLM do LangChain para criar o nosso próprio modelo
from langchain_core.language_models.llms import LLM
from nemoguardrails.llm.providers import register_llm_provider


# 1. Carrega o modelo de classificação
# (Lembre-se de adicionar device=0 dentro do pipeline se estiver usando GPU)
meu_pipeline = pipeline(
    "text-classification", 
    model="xTRam1/safe-guard-classifier", 
)

# 2. Criamos a nossa Classe personalizada seguindo os padrões do LangChain
class MeuModeloSafeguard(LLM):
    
    @property
    def _llm_type(self) -> str:
        # Nome identificador do seu modelo
        return "safeguard"
        
    def _call(self, prompt: str, stop: Optional[List[str]] = None, **kwargs: Any) -> str:
        """Execução síncrona: processa o texto e retorna a label em formato de string."""
        # Roda o texto no modelo do Hugging Face
        resultado = meu_pipeline(prompt)
        
        # O resultado costuma ser algo como [{'label': 'unsafe', 'score': 0.98}]
        # Nós extraímos apenas a palavra ('unsafe' ou 'safe') para o NeMo Guardrails entender
        label = resultado[0]['label'].strip().lower()
        
        if label in ["unsafe", "jailbreak"]:
            return "yes"
        elif label == "safe":
            return "no"
        else:
            # Fallback de segurança caso o modelo retorne algo inesperado
            return "no"

    async def _acall(self, prompt: str, stop: Optional[List[str]] = None, **kwargs: Any) -> str:
        """Execução assíncrona (obrigatória para o NeMo Guardrails)."""
        loop = asyncio.get_running_loop()
        # Roda o método _call síncrono em segundo plano para não travar o NeMo
        return await loop.run_in_executor(
            None, 
            lambda: self._call(prompt, stop, **kwargs)
        )

# 3. Registra a CLASSE (note que passamos MeuModeloSafeguard sem parênteses!)
register_llm_provider("safeguard", MeuModeloSafeguard)