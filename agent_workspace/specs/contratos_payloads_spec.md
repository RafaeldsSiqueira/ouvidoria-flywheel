# 📋 Spec: Contratos de Dados e Regras de Domínio

Esta especificação define os contratos de payloads JSON estritos que serão trafegados entre os componentes do sistema via Pub/Sub e persistidos nas coleções do Firestore.

---

## 🗺️ Mapeamento do Fluxo e Coleções do Firestore

1. **`topico-chamados` (Pub/Sub):** Porta de entrada do sistema.
2. **Coleção `chamados_resolvidos` (Firestore):** Destino de chamados sem risco, classificados automaticamente.
3. **`topico-auditoria` (Pub/Sub):** Canal de desvio para casos críticos.
4. **Coleção `chamados_auditoria` (Firestore):** Casos isolados aguardando revisão humana.
5. **Coleção `logs_treinamento` (Firestore):** Dados enriquecidos após a revisão humana (Mecanismo do Flywheel).

---

## 🗂️ Dicionário de Payloads (Formatos Estritos)

### 1. Entrada de Chamado (`topico-chamados`)
Enviado quando um novo chamado de cliente é gerado.
```json
{
  "chamado_id": "string (UUID v4)",
  "cliente_id": "string",
  "data_criacao": "string (ISO-8601 UTC)",
  "assunto": "string",
  "mensagem": "string"
}
```

### 2. Chamado Resolvido Automaticamente (coleção `chamados_resolvidos`)
Salvo no Firestore quando o chamado não apresenta riscos e é categorizado com sucesso pela IA.
```json
{
  "chamado_id": "string (UUID v4)",
  "cliente_id": "string",
  "data_criacao": "string (ISO-8601 UTC)",
  "assunto": "string",
  "mensagem": "string",
  "analise_ia": {
    "classificacao_sugerida": "DUVIDA | RECLAMACAO | ELOGIO | SUGESTAO",
    "confianca_agente": "float (0.0 a 1.0)",
    "motivo": "string"
  },
  "status_final": "RESOLVIDO_AUTO",
  "data_resolucao": "string (ISO-8601 UTC)"
}
```

### 3. Desvio de Segurança (`topico-auditoria` e coleção `chamados_auditoria`)
Gerado ao interceptar uma exceção de risco jurídico/operacional.
```json
{
  "auditoria_id": "string (UUID v4)",
  "data_desvio": "string (ISO-8601 UTC)",
  "status_revisao": "AGUARDANDO_HUMANO",
  "motivo_desvio": "string (Ex: RISCO_JURIDICO_DETECTADO)",
  "detalhes_seguranca": {
    "gatilhos_encontrados": ["string"],
    "confianca_agente": "float (0.0 a 1.0)"
  },
  "dados_originais": {
    "chamado_id": "string",
    "cliente_id": "string",
    "data_criacao": "string",
    "assunto": "string",
    "mensagem": "string"
  }
}
```

### 4. Log de Retroalimentação (`logs_treinamento`)
Salvo no Firestore após a decisão/correção humana para retroalimentar a IA.
```json
{
  "log_id": "string (UUID)",
  "chamado_id": "string",
  "data_resolucao": "string (ISO-8601 UTC)",
  "analista_responsavel": "string",
  "decisao_humana": {
    "acao": "APROVADO | CORRIGIDO",
    "classificacao_final": "string"
  }
}
```

---

## 🛡️ Regras de Domínio e Condicional de Segurança
A detecção de risco é acionada deterministicamente se o texto do assunto ou da mensagem contiver qualquer um dos seguintes gatilhos (case-insensitive):
- `processo`
- `procon`
- `advogado`
- `justiça`
- `judicial`
- `intimação`
- `processar`
- `danos morais`

Caso contrário, o chamado segue para a chamada à API do Gemini para categorização automática (Ex: `DUVIDA`, `RECLAMACAO`, `ELOGIO`, `SUGESTAO`).
