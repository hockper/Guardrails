# 🛡️ Guardrails (POC)

Uma Prova de Conceito (POC) dedicada ao estudo e avaliação de ferramentas de segurança para LLMs, com foco principal no combate a ataques de **Prompt Injection** e **Jailbreaks**. 

Atualmente, o projeto avalia o desempenho do **NeMo Guardrails** (NVIDIA). A integração com o **Guardrails AI** está mapeada para implementações futuras.

## 🎯 Objetivo
Avaliar o quão eficientes são diferentes configurações de moderação e *safeguards* ao interceptar prompts maliciosos. O projeto conta com um pipeline automatizado que:
1. Executa baterias de testes respeitando limites de API (Rate Limits).
2. Lida com instabilidades de rede (Retries e Checkpoints).
3. Gera relatórios detalhados separando acertos, falhas de segurança (Falsos Negativos) e bloqueios indevidos (Falsos Positivos).

---

## 📂 Estrutura do Projeto

```text
Guardrails/
├── datasets/                     # Datasets de teste (ex: DS_atack_01.csv e .json)
├── .devcontainer/                # Configurações do ambiente de desenvolvimento
├── guardrails-ai/                # (WIP) Futura integração com Guardrails AI
├── nemo-guardrails/              # Módulo principal de avaliação da NVIDIA
│   ├── configs/                  # Contém as subpastas com as configurações do NeMo (.co e .yml)
│   ├── resultados/               # (Gerado automaticamente) JSONs brutos agrupados por lote
│   ├── auditoria_erros/          # (Gerado automaticamente) Relatórios CSV de performance
│   ├── run_evals.py              # Script principal de execução dos testes em lote
│   ├── analisar_resultados.py    # Script de consolidação e auditoria das predições
│   ├── requirements.txt          # Dependências lidas pelo Docker
│   ├── Dockerfile                # Construção da imagem do ambiente
│   └── docker-compose.yml        # Orquestração dos serviços
└── README.md
```

---

## ⚙️ Pré-requisitos e Instalação

**1. Clone o repositório:**
```bash
git clone [https://github.com/hockper/Guardrails.git](https://github.com/hockper/Guardrails.git)
cd Guardrails
```

**2. Configuração da API Key (NVIDIA):**
Para que o NeMo Guardrails consiga se comunicar com os modelos da NVIDIA, você precisa configurar sua chave de API antes de subir o container.
Crie um arquivo chamado `.env` na raiz do módulo `nemo-guardrails/` e adicione sua chave:
```env
NVIDIA_API_KEY=nvapi-sua-chave-aqui
```
*(Nota: Certifique-se de que o arquivo `.env` esteja listado no `.gitignore` para não ser exposto).*

**3. Suba o ambiente Docker:**
Navegue até a pasta do módulo e inicie o container:
```bash
cd nemo-guardrails
docker compose up -d
```
*(Se você estiver abrindo o projeto via GitHub Codespaces, o ambiente será construído e inicializado automaticamente com base na pasta `.devcontainer`).*

---

## 🚀 Como Usar

Com o seu ambiente rodando (seja no terminal do container ou no Codespace), o fluxo de trabalho é dividido em duas etapas: **Execução** e **Análise**.

### Passo 1: Executar os Testes
Para rodar os testes contra os datasets, execute:
```bash
python run_evals.py
```
**O que este script faz?**
* Lê as configurações na pasta `configs/` e busca o dataset mapeado.
* Divide o dataset em pequenos lotes (chunking) para evitar o bloqueio por *Rate Limit* da API da NVIDIA (~40 RPM).
* Salva os resultados temporários em `resultados/`.
* Possui sistema de **Checkpoint**: Se o script for interrompido, ao rodar novamente ele continuará de onde parou.

### Passo 2: Analisar e Auditar os Resultados
Após a conclusão dos testes, execute:
```bash
python analisar_resultados.py
```
**O que este script faz?**
* Varre todos os lotes na pasta `resultados/` e limpa as saídas textuais das LLMs.
* Cruza as predições do modelo com o "Gabarito" (Ground Truth) do dataset CSV original.
* Gera planilhas detalhadas na pasta `auditoria_erros/`, separadas por configuração, contendo:
  * `acertos.csv`: Casos em que o modelo agiu corretamente.
  * `falhas_seguranca_FN.csv`: Casos críticos onde o modelo deixou um ataque passar.
  * `bloqueios_indevidos_FP.csv`: Casos de "paranoia" onde o modelo bloqueou prompts inofensivos.

---

## 🗺️ Roadmap (Próximos Passos)
- [x] Implementar avaliação em lote com NeMo Guardrails.
- [x] Adicionar controle de resiliência (Rate Limit e Retries).
- [x] Criar pipeline de auditoria (Matriz de Confusão).
- [x] Dockerizar ambiente de avaliação.
- [ ] Integrar e avaliar o **Guardrails AI**.
- [ ] Adicionar suporte a LLMs locais (Hugging Face via pipeline) como alternativa à API externa.
```