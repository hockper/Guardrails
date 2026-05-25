import sys
import os

from nemoguardrails import LLMRails
from nemoguardrails.llm.providers import register_llm_provider
from langchain_community.chat_models import FakeListChatModel

DIRETORIO_DO_MOCK = os.path.abspath("/workspaces/Guardrails/nemo-guardrails")

if DIRETORIO_DO_MOCK not in sys.path:
    sys.path.append(DIRETORIO_DO_MOCK)

from mock_llm import MockLLM

def init(app: LLMRails):
    """
    This init function is automatically detected and run by the NeMo CLI
    before it attempts to parse config.yml.
    """

    # 3. Register the mock provider globally
    register_llm_provider("mock_provider", MockLLM)
    