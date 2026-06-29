# 🚀 Plano de Ação: 003_processa_auditoria

## 🎯 Objetivo
Desenvolver a segunda Cloud Function, **processa-auditoria**, utilizando **Python**, aplicando os padrões de **Clean Architecture** e **DDD (Domain-Driven Design)**. O agente será acionado por mensagens do Pub/Sub (`topico-auditoria`), estruturará os dados de desvio conforme o contrato e os persistirá na coleção `chamados_auditoria` do Firestore com o status inicial de `AGUARDANDO_HUMANO`.

---

## 🏗️ Estrutura de Código Sugerida (Clean Arch / DDD)
O código ficará estruturado no diretório da skill `agent_workspace/skills/processa-auditoria/src/`:

```plaintext
src/
├── domain/
│   ├── entities.py          # Entidades do domínio (ex: ChamadoOriginal, Auditoria)
│   └── interfaces.py        # Portas (Interfaces de saída, ex: FirestoreRepositoryInterface)
├── use_cases/
│   └── processar.py         # Caso de uso: coordena a gravação do registro de auditoria no Firestore
├── infrastructure/
│   └── firestore_client.py  # Adaptador de saída para gravar na coleção chamados_auditoria
├── main.py                  # Ponto de entrada (Entrypoint) da Cloud Function
└── requirements.txt         # Dependências (google-cloud-firestore)
```

---

## 📝 Passo a Passo da Execução (DAG Módulos)

### Passo 1: Definição do Domínio (`domain/`)
- Criar a entidade pura `Auditoria` (e o objeto de valor `ChamadoOriginal`) respeitando as propriedades do contrato estrito do JSON.
- Criar a interface abstrata `FirestoreRepositoryInterface` para inversão de dependência.

### Passo 2: Caso de Uso (`use_cases/`)
- Implementar a classe `ProcessarAuditoriaUseCase` que coordena a gravação no repositório.

### Passo 3: Adaptador de Infraestrutura (`infrastructure/`)
- Implementar o adaptador concreto `GcpFirestoreRepository` que persistirá o JSON completo na coleção `chamados_auditoria`.
- **Gargalo Resolvido (Idempotência):** O adaptador deve verificar se a auditoria já existe e, caso exista, ignorar a gravação se o status do chamado já tiver sido alterado pelo analista humano (evitando que reprocessamento resete o chamado de volta para `AGUARDANDO_HUMANO`).

### Passo 4: Entrypoint (`main.py` e `requirements.txt`)
- Criar a função handler `salvar_auditoria(event, context)` que decodifica o evento Pub/Sub (base64) e encaminha ao caso de uso.

### Passo 5: Suíte de Testes Sandbox com Pytest
- Escrever mocks e fakes em memória para testar unitária e integradamente a função sem chamadas reais de rede ao Firestore.

### Passo 6: Deploy e Configuração da Nuvem (Nova Etapa)
- Fornecer o comando de deploy exato para produção:
  ```bash
  gcloud functions deploy processa-auditoria \
      --runtime=python312 \
      --trigger-topic=topico-auditoria \
      --entry-point=processar_auditoria \
      --service-account=sa-ouvidoria-agente@$PROJECT_ID.iam.gserviceaccount.com \
      --region=southamerica-east1
  ```

---

## 🔍 Gargalos Técnicos Mapeados & Resoluções

### 1. Reprocessamento do Pub/Sub vs. Sobrescrita de Status (HITL)
*   **Gargalo:** O Pub/Sub garante a entrega de mensagens *pelo menos uma vez* (at-least-once). Se o Pub/Sub re-entregar a mensagem de desvio após o analista humano já ter revisado e resolvido o caso (mudando para status `RESOLVIDO` ou gerando logs do flywheel), a gravação direta (`.set()`) reiniciaria o status para `AGUARDANDO_HUMANO` e apagaria a revisão humana.
*   **Resolução:** Antes de gravar, a infraestrutura Firestore consulta se o documento com a chave `auditoria_id` existe. Se ele já existir no banco, o sistema ignora a inserção para proteger o trabalho do analista.

### 2. Loops de Retry Infinitos por Payloads Malformados
*   **Gargalo:** Se a mensagem vier sem algum campo essencial do contrato e a função disparar um erro não tratado, o Pub/Sub tentará reenviar a mensagem indefinidamente, estourando as cotas gratuitas.
*   **Resolução:** Captura explícita de `KeyError` e `JSONDecodeError` no entrypoint (`main.py`) para registrar em log e descartar o payload corrompido (retornando sucesso de processamento para realizar o ACK do Pub/Sub).

---

## 🔍 Critérios de Aceitação / Validação
- O documento final salvo no Firestore **deve** conter a estrutura JSON estrita do contrato `topico-auditoria`.
- O status padrão da auditoria inserida **deve** ser `AGUARDANDO_HUMANO`.
- Os testes no sandbox **devem** ser executados localmente e passar com 100% de sucesso.
