import base64
import json
from unittest.mock import patch, MagicMock
from main import processar_auditoria

def test_handler_deve_decodificar_pubsub_e_gravar_auditoria_com_sucesso():
    """
    Testa se o entrypoint principal (processar_auditoria) decodifica corretamente 
    o payload de desvio vindo em base64 do Pub/Sub e chama o orquestrador do caso de uso.
    """
    # 1. Payload de auditoria completo simulando o contrato contratos_payloads_spec
    payload_original = {
        "auditoria_id": "audit-uuid-integracao",
        "data_desvio": "2026-06-29T14:00:00Z",
        "status_revisao": "AGUARDANDO_HUMANO",
        "motivo_desvio": "RISCO_JURIDICO_DETECTADO",
        "detalhes_seguranca": {
            "gatilhos_encontrados": ["procon"],
            "confianca_agente": 1.0
        },
        "dados_originais": {
            "chamado_id": "chamado-uuid-integracao",
            "cliente_id": "cliente-uuid-integracao",
            "data_criacao": "2026-06-29T13:59:00Z",
            "assunto": "Registro no PROCON",
            "mensagem": "Vou ao PROCON reclamar dos meus direitos."
        }
    }
    
    # 2. Codifica em base64
    payload_json_bytes = json.dumps(payload_original).encode('utf-8')
    payload_base64 = base64.b64encode(payload_json_bytes).decode('utf-8')
    
    event = {
        "data": payload_base64
    }
    context = MagicMock()
    
    # 3. Intercepta a execução mockando a chamada ao caso de uso
    with patch("main.use_case") as mock_use_case:
        processar_auditoria(event, context)
        
        # Garante que o caso de uso foi acionado
        mock_use_case.executar.assert_called_once()
        
        # Valida a integridade do mapeamento
        auditoria_recebida = mock_use_case.executar.call_args[0][0]
        assert auditoria_recebida.auditoria_id == "audit-uuid-integracao"
        assert auditoria_recebida.status_revisao == "AGUARDANDO_HUMANO"
        assert auditoria_recebida.dados_originais.chamado_id == "chamado-uuid-integracao"
        assert "procon" in auditoria_recebida.detalhes_seguranca.gatilhos_encontrados
