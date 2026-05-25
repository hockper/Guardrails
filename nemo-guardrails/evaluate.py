# evaluate.py
import os
import time
import pandas as pd
from nemoguardrails import LLMRails, RailsConfig
from nemoguardrails.llm.providers import register_llm_provider

# Importa a classe do nosso arquivo modularizado (mock_llm.py)
from mock_llm import MockLLM

# Registra o modelo customizado no ecossistema do NeMo
register_llm_provider("mock_provider", MockLLM)


def run_evaluation(config_path: str, df: pd.DataFrame, needSleep: bool = True) -> pd.DataFrame:
    """Executa a bateria de testes de Input Check usando as regras do NeMo."""
    
    print(f"Carregando configurações do NeMo em: {config_path}...")
    config = RailsConfig.from_path(config_path)
    rails = LLMRails(config)
    results = []
    
    total_linhas = len(df)
    print(f"Iniciando processamento de {total_linhas} prompts...")
    
    for index, row in df.iterrows():
        prompt = str(row['text']).strip()
        true_label = int(row['label'])
        
        start_time = time.time()
        
        # Envia o prompt para o pipeline do Guardrails
        response = rails.generate(messages=[{"role": "user", "content": prompt}])
        
        latency = time.time() - start_time
        
        resposta_texto = response["content"]
        
        # Lógica de verificação do Mock
        is_blocked = "MENSAGEM NÃO BLOQUEADA" not in resposta_texto
        
        results.append({
            'text': prompt,
            'true_label': true_label,
            'predicted_blocked': 1 if is_blocked else 0,
            'latency_sec': round(latency, 4),
            'resposta_recebida': resposta_texto
        })
        
        if (index + 1) % 10 == 0:
            print(f"Processado {index + 1}/{total_linhas}...")
        
        if needSleep:
            time.sleep(40/60)
            
    return pd.DataFrame(results)

if __name__ == "__main__":
    csv_file_path = "/workspaces/Guardrails/datasets/DS_atack_01.csv" 
    configs_dir = "configs"
    
    try:
        print(f"Lendo o arquivo de dataset {csv_file_path}...")
        # Lendo o dataframe original
        df_original = pd.read_csv(csv_file_path, nrows=3)
        
        # Mapeia todas as pastas dentro do diretório 'configs'
        # Garante que vai pegar apenas diretórios (ignora arquivos soltos)
        config_folders = [
            # f.name for f in os.scandir(configs_dir) if f.is_dir()
            "config_NemoGuard"
        ]
        
        if not config_folders:
            print(f"Nenhuma pasta de configuração encontrada em '{configs_dir}/'.")
            exit()
            
        print(f"Configurações encontradas: {config_folders}\n")
        
        all_results_df = pd.DataFrame()
        
        # Loop para rodar a avaliação em cada configuração encontrada
        for config_name in config_folders:
            config_path = os.path.join(configs_dir, config_name)
            print(f"{'='*50}")
            print(f"Iniciando avaliação para: {config_name}")
            print(f"{'='*50}")
            
            needSleep = False
            if config_name == "config_NemoGuard":
                needSleep = True

            # Passa uma cópia do df para evitar qualquer problema de alteração em memória
            df_results = run_evaluation(config_path, df_original.copy(), needSleep)
            
            # Adiciona uma coluna com o nome da configuração para rastreabilidade
            df_results.insert(0, 'config_name', config_name)
            
            # Mostra preview dessa rodada
            print(f"\n[Concluído: {config_name}]")
            print(df_results[['config_name', 'true_label', 'predicted_blocked', 'latency_sec']].head(5))
            
            # Salva o resultado individual (opcional, mas recomendado)
            output_file = f"resultados_{config_name}.csv"
            df_results.to_csv(output_file, index=False)
            print(f"-> Salvo: {output_file}\n")
            
            # Concatena no DataFrame geral
            all_results_df = pd.concat([all_results_df, df_results], ignore_index=True)
            
        print(f"{'='*50}")
        print("[Avaliação Total Concluída]")
        
        # Salva o compilado de todas as configs em um único arquivo
        final_output = "resultados_avaliacao_completa.csv"
        all_results_df.to_csv(final_output, index=False)
        print(f"Resultados compilados salvos em '{final_output}'.")
        
    except FileNotFoundError as e:
        print(f"Erro de arquivo/diretório: {e}")
    except KeyError as e:
        print(f"Erro de coluna: O CSV precisa ter as colunas 'text' e 'label'. Detalhe: {e}")