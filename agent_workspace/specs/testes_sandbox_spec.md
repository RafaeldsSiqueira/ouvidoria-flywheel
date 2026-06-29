# 🧪 Spec: Estratégia de Testes Sandbox com Pytest

Esta especificação define como os testes automatizados serão estruturados e executados localmente para garantir o comportamento correto do fluxo (triagem e auditoria) sem custos e sem dependência de recursos ativos na nuvem (GCP).

---

## 📂 Estrutura de Pastas de Testes

Os testes serão mantidos de forma modular dentro de cada Skill correspondente para facilitar o empacotamento e a CI/CD:

```plaintext
agent_workspace/skills/agente-classificador/
├── src/
│   ├── domain/
│   ├── use_cases/
│   └── infrastructure/
└── tests/
    ├── conftest.py            # Fixtures do Pytest (Mocks globais da GCP e Gemini)
    ├── test_domain.py         # Testes unitários das regras de negócio do Domínio
    ├── test_use_cases.py      # Testes de fluxo e lógica do Caso de Uso (com Mocks)
    └── test_integration.py    # Teste de integração do Handler da Cloud Function (main.py)
```

---

## 🎛️ Mocks e Fakes de Infraestrutura (`conftest.py`)

Para rodar de forma 100% gratuita localmente, substituiremos os SDKs reais por Mocks.

### 1. Mock do Firestore
Simula a gravação e recuperação de documentos em memória.
```python
class FakeFirestoreClient:
    def __init__(self):
        self.db = {}

    def salvar_resolvido(self, chamado_id: str, payload: dict):
        self.db[f"chamados_resolvidos/{chamado_id}"] = payload

    def salvar_auditoria(self, auditoria_id: str, payload: dict):
        self.db[f"chamados_auditoria/{auditoria_id}"] = payload
```

### 2. Mock do Pub/Sub
Simula a publicação de mensagens monitorando os payloads disparados.
```python
class FakePubSubPublisher:
    def __init__(self):
        self.mensagens_publicadas = []

    def publicar(self, topico: str, payload: dict):
        self.mensagens_publicadas.append({"topico": topico, "payload": payload})
```

### 3. Mock da API do Gemini (AI Studio)
Evita chamadas HTTP reais à API do Gemini, retornando respostas consistentes baseadas no input do teste.
```python
class FakeGeminiClient:
    def classificar(self, chamado: dict) -> dict:
        return {
            "classificacao_sugerida": "DUVIDA",
            "confianca_agente": 0.85,
            "motivo": "O cliente fez uma pergunta sobre o funcionamento do produto."
        }
```

---

## 🔄 Fases de Teste (Execução por Etapas)

### Fase 1: Validação de Regras do Domínio (`test_domain.py`)
Valida as regras determinísticas de desvio por termos jurídicos.
*   **Caso de Teste 1:** Entrada contendo `"Fui ao PROCON"` deve retornar `Risco Jurídico Detectado = True`.
*   **Caso de Teste 2:** Entrada contendo `"Gostei do atendimento"` deve retornar `Risco Jurídico Detectado = False`.

### Fase 2: Validação de Casos de Uso (`test_use_cases.py`)
Valida se a coordenação do fluxo está correta (Cenário A vs Cenário B).
*   **Cenário A (Aprovação e Resolução Sem Risco):** Garante que, ao não detectar termos críticos de risco, o caso de uso invoca o cliente do Gemini para obter a análise da IA, valida se o payload de saída está em conformidade com o contrato de `chamados_resolvidos` (contendo `analise_ia`, `status_final = RESOLVED_AUTO` e data de resolução) e persiste no Firestore. Adicionalmente, assegura que nada foi enviado ao `topico-auditoria`.
*   **Cenário B (Bloqueio com Desvio por Risco):** Garante que, caso ocorra a detecção de termos críticos de risco, o caso de uso cancela a etapa do Gemini, empacota os dados originais no formato de auditoria (`AGUARDANDO_HUMANO`) e publica a mensagem no `topico-auditoria`. Assegura também que nada foi gravado na coleção `chamados_resolvidos`.

### Fase 3: Integração do Handler (`test_integration.py`)
Simula a recepção de um evento real de Pub/Sub em base64 e valida se a Cloud Function processa com sucesso (retorna status `200` ou executa sem exceções).

---

## 🚀 Como Executar os Testes
A execução será feita dentro da pasta da Skill usando o ambiente virtual (`venv`):
```bash
# Entrar no diretório da skill
cd agent_workspace/skills/agente-classificador

# Instalar dependências de testes
pip install pytest pytest-mock

# Executar a suíte de testes
pytest -v
```
