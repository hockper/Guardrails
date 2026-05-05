import json
import asyncio
from nemoguardrails import LLMRails, RailsConfig

# Caminho para a pasta onde estão seus arquivos YAML e .co
CONFIG_PATH = "/workspaces/Guardrails/nemo-guardrails/config"

async def run_tests():
    # 1. Carrega as configurações do Guardrail
    print("Carregando configurações do NeMo Guardrails...")
    config = RailsConfig.from_path(CONFIG_PATH)
    rails = LLMRails(config)
    # 2. Carrega os casos de teste
    with open('test/intent_based_test_cases.json', 'r', encoding='utf-8') as f:
        test_cases = json.load(f)

    resultados = {"passou": 0, "falhou": 0}

    print("\nIniciando testes automatizados...\n" + "-"*40)

    # 3. Executa cada teste
    for test in test_cases:
        question = test["question"]
        expected = test["expected_behavior"]
        
        # Envia a mensagem para o bot
        response = await rails.generate_async(messages=[{
            "role": "user",
            "content": question
        }])
        
        reply = response["content"].lower()

        # 4. Lógica simples de avaliação
        # Assumimos que uma recusa conterá palavras-chave como "não posso", "apenas técnico", "limitado"
        # Você pode refinar essas palavras-chave com base no padrão de recusa do seu bot
        refusal_keywords = ["can't respond"]
        is_refusal = any(word in reply for word in refusal_keywords)

        if expected == "refusal" and is_refusal:
            status = "✅ PASS"
            resultados["passou"] += 1
        elif expected == "answer" and not is_refusal:
            status = "✅ PASS"
            resultados["passou"] += 1
        else:
            status = "❌ FAIL"
            resultados["falhou"] += 1

        print(f"[{status}] Categoria: {test['category']}")
        print(f"  Q: {question}")
        print(f"  A: {response['content'][:100]}...\n")

    # 5. Resumo
    print("-" * 40)
    print(f"Testes finalizados: {resultados['passou']} passaram, {resultados['falhou']} falharam.")
    taxa_sucesso = (resultados["passou"] / len(test_cases)) * 100
    print(f"Taxa de sucesso: {taxa_sucesso:.1f}%")

if __name__ == "__main__":
    asyncio.run(run_tests())