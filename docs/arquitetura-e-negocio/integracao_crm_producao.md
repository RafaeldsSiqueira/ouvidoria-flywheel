# 🔌 Integração Prática com CRMs Corporativos em Produção

Este documento detalha como acoplar a arquitetura de ouvidoria baseada em eventos a plataformas de CRM de mercado (como **Zendesk**, **Salesforce**, **HubSpot**) ou sistemas internos legados.

---

## 📐 O Fluxo de Integração

A integração baseia-se em dois mecanismos fundamentais da Web moderna: **Webhooks** (para envio de dados do CRM à nuvem) e **APIs REST** (para atualização de dados da nuvem de volta ao CRM).

```
   [ CRM de Mercado ] ──(1. Webhook HTTP POST)──> [ GCP API Gateway ]
          ▲                                               │
          │ (4. Chamada de API REST - PUT)                ▼
          └────────────────────────────────── [ Pub/Sub e Cloud Functions ]
```

---

## 📥 1. Entrada de Dados: Do CRM para o Pub/Sub
Quando um cliente abre um chamado no CRM, o sistema precisa notificar nossa arquitetura GCP.

1.  **Configuração de Webhook no CRM:**
    *   Nas configurações do CRM (ex: Zendesk Admin > Webhooks), cria-se uma regra: *"Toda vez que um ticket for criado ou atualizado com uma nova mensagem de cliente, envie um POST HTTP para o endpoint `https://meu-endpoint-gcp.com/chamado`"*.
2.  **API Gateway ou Cloud Function HTTP (Ingestão):**
    *   No GCP, criamos um ponto de entrada HTTP simples (API Gateway ou Cloud Function HTTP).
    *   Ela recebe o JSON bruto enviado pelo webhook do CRM, extrai os campos necessários (ID do ticket, e-mail do cliente, assunto, mensagem), formata conforme o nosso contrato de payload (`topico-chamados`) e publica a mensagem no tópico Pub/Sub.

---

## 📤 2. Saída de Dados: Da Nuvem de Volta para o CRM
Após o processamento pelas Cloud Functions (`agente-classificador` ou `processa-auditoria`), o resultado final é injetado de volta no CRM.

### Cenário A (Chamado Resolvido pela IA):
1.  Um gatilho do Firestore escuta a inserção de novos chamados na coleção `chamados_resolvidos`.
2.  Uma Cloud Function de integração é acionada e faz uma chamada à **API REST do CRM** (ex: `PUT /api/v2/tickets/{ticket_id}.json` no Zendesk) para:
    *   Definir tags de classificação (ex: `categoria:elogio`, `ia_confianca:0.95`).
    *   Adicionar um comentário interno com a justificativa gerada pelo Gemini (`motivo`).
    *   Mudar o status do chamado no CRM para **Resolvido** (fechamento automático) ou associá-lo a uma resposta FAQ padrão.

### Cenário B (Desvio de Segurança / HITL):
1.  A detecção de risco determina que o chamado é crítico e ele é enviado à coleção `chamados_auditoria`.
2.  Uma Cloud Function faz uma chamada à **API REST do CRM** para:
    *   Setar a prioridade do chamado no CRM para **Alta/Urgente**.
    *   Adicionar uma tag de alerta (ex: `risco_juridico_detectado`).
    *   **Redirecionar de Fila:** Alterar o grupo de atendimento do chamado no CRM (ex: move do grupo de "Suporte Comum" para o grupo "Time de Legal & Compliance"). Os analistas humanos continuam respondendo e auditando o caso na própria tela que já usam diariamente no CRM.

---

## 🔍 Resumo dos Pré-requisitos Técnicos
Para ligar essa arquitetura em qualquer plataforma corporativa, você necessita apenas de:
1.  **Capacidade de Webhook do CRM:** Para notificar e enviar chamados ao GCP em tempo real.
2.  **Credenciais de API REST do CRM:** (Chave de API ou Token OAuth) salvas com segurança no Secret Manager, permitindo que as Cloud Functions atualizem os chamados de volta.

---

## 🛡️ Mapeamento de Payloads e o Padrão Adapter (Clean Architecture)

Como cada CRM envia e espera dados em formatos completamente diferentes, o uso de **Clean Architecture** é fundamental para manter nosso sistema isolado e robusto:

1.  **A Nuvem é o Core:** As nossas coleções do Firestore e tópicos do Pub/Sub possuem contratos rígidos (`contratos_payloads_spec.md`) que **nunca** mudam, independente do CRM utilizado.
2.  **O Papel do Adapter (Adaptador):**
    *   **Na Ingestão (Entrada):** A Cloud Function HTTP de entrada atua como um tradutor. Se o Zendesk envia `ticket.subject` e o Salesforce envia `Case.Subject`, a função traduz ambos para o campo padronizado `assunto`.
    *   **Na Integração (Saída):** O adaptador de infraestrutura traduz nossa entidade de domínio neutra para o JSON esperado pela API do CRM. 
    *   *Exemplo:* Se migrarmos do Zendesk para o Salesforce, os nossos casos de uso, lógica de risco e classificação por IA **não mudam**. Apenas escrevemos um novo arquivo em `infrastructure/salesforce_client.py` que traduz `classificacao_sugerida` para o campo customizado do Salesforce (ex: `Category__c`).

---

## ⚡ Dinamismo e Princípio Open-Closed (SOLID)

A maior vantagem dessa arquitetura é o seu **dinamismo de extensibilidade**:
*   Para conectar uma nova plataforma à ouvidoria, **não alteramos uma única linha da lógica de negócios ou do classificador de IA**.
*   A única tarefa necessária é **criar um novo arquivo `.py`** (ex: `jira_client.py` ou `hubspot_client.py`) dentro do diretório `infrastructure/` que respeite a interface correspondente.
*   Isso é a aplicação direta do **Princípio do Aberto/Fechado (Open-Closed Principle - OCP)** do SOLID: o sistema está *aberto para extensão* (suporta novos CRMs apenas adicionando arquivos) mas *fechado para modificação* (não altera o core estável e já testado).

---

## 🔄 Sincronização de Estado: Quem resolve o Chamado (HITL)?

A direção da sincronização bidirecional de dados depende diretamente de onde o analista especializado toma a decisão de auditoria no dia a dia da empresa:

### Cenário 1: O Analista resolve diretamente dentro do CRM (Fluxo nativo)
O analista trabalha diretamente no painel do CRM corporativo (ex: Zendesk/Salesforce) e altera o status do ticket para "Resolvido".
*   **Fluxo de Controle:** O CRM é a **fonte da verdade** do início da ação.
*   **Mecanismo:** Ao salvar o ticket no CRM, a plataforma envia um **segundo Webhook** (evento de "Ticket Resolvido") para o GCP. A Cloud Function correspondente decodifica o payload de fechamento, grava o log estruturado na coleção `logs_treinamento` (alimentando o Data Flywheel) e atualiza o status do chamado em `chamados_auditoria` no Firestore para `RESOLVIDO`.
*   *Nota:* Não é necessário chamar nenhuma API do CRM neste fechamento, pois a ação original partiu do próprio CRM.

### Cenário 2: O Analista resolve no Painel Customizado da GCP (Streamlit/React)
O analista não tem acesso à conta do CRM corporativo (seja por controle rígido de segurança de dados ou para economizar em licenças de agentes). Ele utiliza uma interface web própria conectada ao Firestore.
*   **Fluxo de Controle:** A GCP/Firestore é a **fonte da verdade** do início da ação.
*   **Mecanismo:** Quando o analista clica em "Resolver" no painel customizado, o status do documento em `chamados_auditoria` é atualizado para `RESOLVIDO` no Firestore. Essa mudança aciona um Firestore Trigger (Cloud Function) que **faz uma chamada de API REST (HTTP PUT) de volta ao CRM**, notificando: *"O analista jurídico aprovou a auditoria do chamado #ID. Altere o status deste ticket para Resolvido no CRM e registre o comentário final no ticket"*.
*   *Nota:* Esse fluxo de controle inverso garante que os dois sistemas fiquem sincronizados de forma autônoma.

---

## 💡 Sugestão de Aplicação Prática: Autoatendimento vs. Contato Humano Emocional

A tomada de decisão estratégica sobre responder automaticamente ou direcionar a um humano baseia-se no nível de sensibilidade e risco do chamado:

### 🟢 Para Chamados Sem Risco (Cenário A): Automação Baseada em Conhecimento (Auto-Reply)
Em chamados comuns de triagem bem-sucedida, o sistema reduz o esforço do time a zero:
1.  **Coleção `base_conhecimento` (Firestore):** Armazena templates de respostas parametrizadas vinculadas às categorias (ex: templates específicos para `DUVIDA`, `ELOGIO` ou `SUGESTAO`).
2.  **Disparo Automatizado:** Um gatilho do Firestore aciona uma Cloud Function de notificação. Ela lê a classificação da IA, busca o template correspondente na base de conhecimento, substitui variáveis dinâmicas (como nome do cliente e número do chamado) e envia o e-mail ou mensagem direta (WhatsApp/SMS) de resposta ao cliente de forma instantânea.

### 🔴 Para Chamados de Risco (Cenário B): Contato Humano Personalizado (HITL)
Em chamados com termos críticos (risco jurídico/operacional), a automação de resposta é **expressamente evitada**:
*   **A Abordagem:** O sistema realiza apenas o roteamento automático do ticket para a fila de atendimento prioritário no CRM.
*   **A Justificativa:** Casos de alta fricção (ex: ameaças de processos judiciais, danos morais ou PROCON) necessitam obrigatoriamente de empatia, negociação, tato emocional e tomadas de decisão que a inteligência artificial não é capaz de simular de forma segura. O contato deve ser 100% conduzido por um analista humano especializado para mitigar o atrito e proteger a relação comercial com o cliente.

