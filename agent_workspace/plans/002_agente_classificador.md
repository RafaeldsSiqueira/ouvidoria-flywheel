# 🚀 Plano de Ação: 002_agente_classificador

## 🎯 Objetivo
Desenvolver o **Agente Classificador** (Cloud Function 1) utilizando **Python**, aplicando os padrões de **Clean Architecture** e **DDD (Domain-Driven Design)**. O agente será acionado por mensagens do Pub/Sub (`topico-chamados`), avaliará o risco de forma determinística e, se seguro, classificará o chamado usando a API do Gemini (Google AI Studio) e salvará no Firestore. Se contiver risco, desviará o chamado para o `topico-auditoria`.

---

## 🏗️ Estrutura de Código Sugerida (Clean Arch / DDD)
O código ficará estruturado no diretório da skill `agent_workspace/skills/agente-classificador/src/`:

```plaintext
src/
├── domain/
│   ├── entities.py          # Definição das entidades do domínio (ex: Chamado, Classificacao)
│   ├── rules.py             # Regras de negócio puras (ex: detecção determinística de termos de risco)
│   └── interfaces.py        # Portas (Interfaces de saída/adaptadores, ex: PublisherInterface)
├── use_cases/
│   └── classificar.py       # Caso de uso: recebe o chamado, decide fluxo (A ou B) e executa
├── infrastructure/
│   ├── pubsub_client.py     # Adaptador de saída para publicar no Pub/Sub
│   ├── firestore_client.py  # Adaptador de saída para gravar no Firestore
│   └── gemini_client.py     # Adaptador de saída para interagir com o Google AI Studio
├── main.py                  # Ponto de entrada (Entrypoint) da Cloud Function
└── requirements.txt         # Dependências (google-cloud-pubsub, google-cloud-firestore, google-generativeai)
```

---

## 📝 Passo a Passo da Execução (DAG Módulos)

### Passo 1: Definição do Domínio (`domain/`)
- Escrever entidades puras Python (usando `dataclasses`) livres de qualquer framework ou SDK.
- Implementar a regra de filtragem de termos de risco de forma determinística:
  - Gatilhos: `"processo", "procon", "advogado", "justiça", "judicial", "intimação", "processar", "danos morais"`.

### Passo 2: Definição dos Casos de Uso (`use_cases/`)
- Implementar a classe `ProcessarChamadoUseCase` que orchestrará o fluxo:
  1. Analisar se o chamado possui risco.
  2. **Caso B (Com Risco):** Encapsular dados no contrato de auditoria e invocar o adaptador do Pub/Sub (`topico-auditoria`).
  3. **Caso A (Sem Risco):** Chamar o classificador IA do Gemini para rotular a categoria e persistir no Firestore (`chamados_resolvidos`).

### Passo 3: Implementação da Infraestrutura (`infrastructure/`)
- **`gemini_client.py`:** Utilizar a biblioteca `google-generativeai` configurada via API Key externa para solicitar classificação sob formato estrito (DUVIDA, RECLAMACAO, ELOGIO, SUGESTAO).
- **`firestore_client.py`:** Gravar documentos na coleção `chamados_resolvidos`.
- **`pubsub_client.py`:** Publicar desvios no tópico `topico-auditoria`.

### Passo 4: Entrypoint e Configuração (`main.py` e `requirements.txt`)
- Criar a função handler `classificar_chamado(event, context)` que lê a mensagem vinda do Pub/Sub (decodificando base64), inicializa as dependências de infraestrutura e executa o caso de uso.

### Passo 5: Testes Locais e Mocks
- Criar scripts de simulação local na pasta `scratch/` para validar o classificador e o detector de risco sem necessidade de deploy no GCP (usando mocks do Firestore e Pub/Sub).

---

## 🔍 Critérios de Aceitação / Validação
- Chamados contendo "procon" ou "justiça" **devem** ser publicados no `topico-auditoria`.
- Chamados comuns **devem** ser persistidos na coleção `chamados_resolvidos` com uma categoria válida sugerida pelo Gemini.
- Chave do Gemini **não deve** estar hardcoded no código (usar variáveis de ambiente/Secrets).
