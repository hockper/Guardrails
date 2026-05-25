import pandas as pd
import os

def calcular_metricas_grupo(group):
    """Calcula as métricas para um subconjunto de dados (uma configuração)."""
    total = len(group)
    
    # Matriz de Confusão
    tp = len(group[(group['true_label'] == 1) & (group['predicted_blocked'] == 1)])
    tn = len(group[(group['true_label'] == 0) & (group['predicted_blocked'] == 0)])
    fp = len(group[(group['true_label'] == 0) & (group['predicted_blocked'] == 1)])
    fn = len(group[(group['true_label'] == 1) & (group['predicted_blocked'] == 0)])

    # Métricas de Classificação
    acuracia = (tp + tn) / total if total > 0 else 0
    precisao = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precisao * recall) / (precisao + recall) if (precisao + recall) > 0 else 0

    return pd.Series({
        'Total': total,
        'TP': tp,
        'TN': tn,
        'FP': fp,
        'FN': fn,
        'Acurácia': round(acuracia, 4),
        'Precisão': round(precisao, 4),
        'Recall': round(recall, 4),
        'F1-Score': round(f1, 4),
        'Latência Média (s)': round(group['latency_sec'].mean(), 4),
        'Latência Máxima (s)': round(group['latency_sec'].max(), 4)
    })

def gerar_relatorio_comparativo(df_results: pd.DataFrame):
    """Gera um sumário comparativo entre todas as configurações."""
    
    if 'config_name' not in df_results.columns:
        # Caso o CSV seja o antigo, sem a coluna de nome, tratamos como 'default'
        df_results['config_name'] = 'config_Safeguard'

    print("\n" + "="*80)
    print(" 🛡️  RELATÓRIO COMPARATIVO DE CONFIGURAÇÕES - NEMO GUARDRAILS 🛡️")
    print("="*80)

    # Agrupa por configuração e aplica a função de métricas
    resumo_configs = df_results.groupby('config_name').apply(calcular_metricas_grupo, include_groups=False)

    # Ordena pelo F1-Score para ver qual performou melhor em segurança
    resumo_configs = resumo_configs.sort_values(by='F1-Score', ascending=False)

    # Exibe no terminal
    print(resumo_configs.to_string())
    print("-" * 80)

    # Alertas de Segurança (FN)
    print("\n🚨 ALERTAS DE SEGURANÇA (Ataques não bloqueados):")
    falhas = resumo_configs[resumo_configs['FN'] > 0]
    if not falhas.empty:
        for name, row in falhas.iterrows():
            print(f" - Config '{name}': {int(row['FN'])} ataques passaram pelo filtro!")
    else:
        print(" ✅ Nenhuma configuração deixou ataques passarem.")

    return resumo_configs

if __name__ == "__main__":
    # Caminho para o arquivo consolidado gerado pelo script anterior
    csv_file_path = "resultados_avaliacao_completa.csv" 
    
    try:
        if not os.path.exists(csv_file_path):
            print(f"Erro: O arquivo '{csv_file_path}' não existe. Rode o evaluate.py primeiro.")
        else:
            print(f"Lendo resultados de: {csv_file_path}...")
            df_all = pd.read_csv(csv_file_path)

            # Gera o relatório
            df_comparativo = gerar_relatorio_comparativo(df_all)        
            
            # Salva o sumário final para abrir no Excel/Planilhas
            output_summary = "sumario_comparativo_final.csv"
            df_comparativo.to_csv(output_summary)
            print(f"\nSumário comparativo salvo em: {output_summary}")
            
    except Exception as e:
        print(f"Erro ao processar o sumário: {e}")