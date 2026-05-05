import os
import subprocess
import json
import time
import shutil
from pathlib import Path

# --- Configurações Principais ---
PASTA_CONFIGS = "configs"
ARQUIVO_DATASET = "/workspaces/Guardrails/datasets/DS_atack_01.json"
PASTA_RESULTADOS = "resultados"
TIPO_AVALIACAO = "moderation" 

# --- Configurações de Controle de API (Rate Limit e Resiliência) ---
TAMANHO_LOTE = 10       
PAUSA_ENTRE_LOTES = 15 
MAX_TENTATIVAS = 3     # Quantas vezes ele vai tentar refazer um lote que deu "null"

def lote_tem_resposta_nula(pasta_lote):
    """Lê os arquivos JSON gerados na pasta do lote e verifica se a API retornou null."""
    caminho = Path(pasta_lote)
    arquivos_json = list(caminho.glob("*.json"))
    
    # Se não gerou arquivo nenhum, consideramos como falha/nulo
    if not arquivos_json:
        return True 

    for arq in arquivos_json:
        try:
            with open(arq, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                for item in dados:
                    # Pega todas as chaves exceto o 'prompt'
                    respostas = {k: v for k, v in item.items() if k != 'prompt'}
                    
                    # Se não houver resposta, ou a resposta for None/null, falhou
                    if not respostas:
                        return True
                    for valor in respostas.values():
                        if valor is None or str(valor).strip().lower() == "null":
                            return True
        except json.JSONDecodeError:
            return True # Arquivo corrompido é tratado como falha

    return False # Tudo certo, nenhuma resposta nula encontrada!

def limpar_pasta_lote(pasta_lote):
    """Remove a pasta do lote e seus conteúdos para garantir um retry limpo."""
    if os.path.exists(pasta_lote):
        shutil.rmtree(pasta_lote)

def executar_avaliacoes_em_lote():
    caminho_configs = Path(PASTA_CONFIGS)
    if not caminho_configs.exists() or not caminho_configs.is_dir():
        print(f"❌ Erro: A pasta '{PASTA_CONFIGS}' não foi encontrada.")
        return

    if not Path(ARQUIVO_DATASET).exists():
        print(f"❌ Erro: O dataset '{ARQUIVO_DATASET}' não foi encontrado.")
        return

    with open(ARQUIVO_DATASET, 'r', encoding='utf-8') as f:
        dataset_completo = json.load(f)
        
    tamanho_dataset = len(dataset_completo)
    print(f"📄 Dataset carregado. Total de prompts: {tamanho_dataset}")
    
    lotes = [dataset_completo[i:i + TAMANHO_LOTE] for i in range(0, tamanho_dataset, TAMANHO_LOTE)]
    print(f"📦 O dataset foi dividido em {len(lotes)} lotes.\n")

    subpastas_config = [p for p in caminho_configs.iterdir() if p.is_dir()]

    if not subpastas_config:
        print(f"⚠️ Nenhuma subpasta de configuração encontrada dentro de '{PASTA_CONFIGS}'.")
        return

    print(f"🔍 Encontradas {len(subpastas_config)} configurações para testar.\n")

    for pasta_config in subpastas_config:
        nome_config = pasta_config.name
        print(f"🚀 Iniciando avaliação para a configuração: **{nome_config}**")

        for idx_lote, lote in enumerate(lotes):
            pasta_saida = Path(PASTA_RESULTADOS) / f"{nome_config}_ataques" / f"lote_{idx_lote + 1}"
            
            # --- 1. LÓGICA DE CONTINUAR DE ONDE PAROU ---
            if pasta_saida.exists():
                if not lote_tem_resposta_nula(pasta_saida):
                    print(f"   ⏭️  Lote {idx_lote + 1} já foi processado com sucesso anteriormente. Pulando...")
                    continue
                else:
                    print(f"   ♻️  Lote {idx_lote + 1} incompleto ou com 'null' detectado em run anterior. Refazendo...")
                    limpar_pasta_lote(pasta_saida) # Limpa para refazer do zero

            print(f"   ▶️ Processando lote {idx_lote + 1} de {len(lotes)}...")
            
            arquivo_lote_temp = f"temp_lote_{nome_config}.json"
            with open(arquivo_lote_temp, 'w', encoding='utf-8') as f:
                json.dump(lote, f, ensure_ascii=False, indent=2)

            comando = [
                "nemoguardrails", "eval", "rail", TIPO_AVALIACAO,
                f"--config={pasta_config}",
                f"--dataset-path={arquivo_lote_temp}",
                f"--output-dir={pasta_saida}",
                "--no-check-output"
            ]

            # --- 2. LÓGICA DE RETRY E VALIDAÇÃO DE NULLS ---
            sucesso_no_lote = False
            tentativas = 0

            while not sucesso_no_lote and tentativas < MAX_TENTATIVAS:
                tentativas += 1
                try:
                    resultado = subprocess.run(
                        comando,
                        capture_output=True, 
                        text=True,           
                        check=True           
                    )

                    # Verifica se as saídas contêm "null"
                    if lote_tem_resposta_nula(pasta_saida):
                        print(f"      ⚠️ Resposta 'null' da API detectada na tentativa {tentativas}/{MAX_TENTATIVAS}.")
                        limpar_pasta_lote(pasta_saida)
                        
                        if tentativas < MAX_TENTATIVAS:
                            pausa_retry = PAUSA_ENTRE_LOTES * 2
                            print(f"      ⏳ API sobrecarregada. Pausando por {pausa_retry}s antes de tentar de novo...")
                            time.sleep(pausa_retry)
                        else:
                            print(f"      ❌ Lote {idx_lote + 1} falhou permanentemente após {MAX_TENTATIVAS} tentativas.")
                    else:
                        sucesso_no_lote = True
                        for linha in resultado.stdout.split('\n'):
                            if "of samples" in linha:
                                print(f"      📊 {linha.strip()}")
                        print(f"   ✅ Lote {idx_lote + 1} concluído com sucesso na tentativa {tentativas}.")
                            
                except subprocess.CalledProcessError as e:
                    print(f"   ❌ Falha crítica no subprocesso do lote {idx_lote + 1} (Tentativa {tentativas}).")
                    limpar_pasta_lote(pasta_saida)
                    if tentativas < MAX_TENTATIVAS:
                        time.sleep(PAUSA_ENTRE_LOTES * 2)

            # Remove o arquivo temporário
            if os.path.exists(arquivo_lote_temp):
                os.remove(arquivo_lote_temp)

            # Pausa padrão se não for o último lote
            if idx_lote < len(lotes) - 1 and sucesso_no_lote: 
                time.sleep(PAUSA_ENTRE_LOTES)
        
        print(f"🏁 Configuração '{nome_config}' finalizada!")
        print(f"⏳ Pausa extra de {PAUSA_ENTRE_LOTES * 2}s antes de iniciar a próxima configuração...\n")
        time.sleep(PAUSA_ENTRE_LOTES * 2)
        print("-" * 50)

    print("🎉 Todas as avaliações foram concluídas por completo!")

if __name__ == "__main__":
    executar_avaliacoes_em_lote()