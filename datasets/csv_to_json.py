import csv
import json
from pathlib import Path

ARQUIVO_CSV = "DS_atack_01.csv"
ARQUIVO_JSON = "DS_atack_01.json"

def converter_csv_para_json():
    print(f"🔄 Lendo o arquivo {ARQUIVO_CSV}...")
    dados_formatados = []
    
    if not Path(ARQUIVO_CSV).exists():
        print(f"❌ Erro: O arquivo '{ARQUIVO_CSV}' não foi encontrado.")
        return

    with open(ARQUIVO_CSV, mode='r', encoding='utf-8') as arquivo_csv:
        leitor = csv.DictReader(arquivo_csv)
        
        for linha in leitor:
            # Tenta pegar a coluna 'question', 'prompt' ou a primeira que aparecer
            texto_pergunta = linha.get("question") or linha.get("prompt")
            if not texto_pergunta:
                texto_pergunta = list(linha.values())[0]
            
            dados_formatados.append({"question": texto_pergunta})
            
    with open(ARQUIVO_JSON, mode='w', encoding='utf-8') as arquivo_json:
        json.dump(dados_formatados, arquivo_json, indent=2, ensure_ascii=False)
        
    print(f"✅ Sucesso! {len(dados_formatados)} ataques foram salvos em '{ARQUIVO_JSON}'.")

if __name__ == "__main__":
    converter_csv_para_json()