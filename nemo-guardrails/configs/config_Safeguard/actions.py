import asyncio
from typing import Any, List, Optional
from transformers import pipeline
from langchain_core.language_models.llms import LLM
from nemoguardrails.llm.providers import register_llm_provider
from nemoguardrails.actions import action

print("Carregando o modelo de Safeguard na memória (isso acontece só uma vez)...")
# 1. Carregamos o modelo fora da classe para reaproveitá-lo em todas as requisições
guard_classifier = pipeline(
    "text-classification", 
    model="xTRam1/safe-guard-classifier", 
)

# 2. Sua Classe personalizada
class Safeguard(LLM):
    
    @property
    def _llm_type(self) -> str:
        return "safeguard"
        
    def _call(self, prompt: str, stop: Optional[List[str]] = None, **kwargs: Any) -> str:
        """Execução síncrona: processa o texto e retorna a label em formato de string."""
        # Usa o pipeline já carregado na memória
        resultado = guard_classifier(prompt)
        
        label = resultado[0]['label'].strip().lower()
        
        # Retornamos STRINGS porque o LangChain exige que _call retorne texto
        if label in ["unsafe", "jailbreak"]:
            return "unsafe"
        elif label == "safe":
            return "safe"
        else:
            return "safe"

    async def _acall(self, prompt: str, stop: Optional[List[str]] = None, **kwargs: Any) -> str:
        """Execução assíncrona (obrigatória para o NeMo Guardrails)."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, 
            lambda: self._call(prompt, stop, **kwargs)
        )

# 3. O lugar para registrar o provider é aqui!
register_llm_provider("safeguard", Safeguard)


# 4. Criamos a Ação Customizada que o Colang vai chamar no fluxo
# Instanciamos o seu modelo
safeguard_llm = Safeguard()

@action(is_system_action=True, name="check_local_jailbreak")
async def check_local_jailbreak(user_input: str) -> bool:
    """
    Usa o modelo Safeguard para avaliar o input.
    Retorna True (é jailbreak/unsafe) ou False (é seguro).
    """
    try:
        # Usamos o método ainvoke do LangChain para chamar o modelo de forma assíncrona
        resultado = await safeguard_llm.ainvoke(user_input)
        
        # Se a string retornada for "unsafe", retorna True (bloqueia o fluxo)
        return resultado == "unsafe"
    
    except Exception as e:
        print(f"Erro ao processar classificador Safeguard: {e}")
        return False