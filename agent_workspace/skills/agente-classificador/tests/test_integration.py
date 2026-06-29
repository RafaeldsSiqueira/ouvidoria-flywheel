import base64
import json
from unittest.mock import patch, MagicMock
from main import classificar_chamado

def test_handler_deve_decodificar_pubsub_e_executar_fluxo_com_sucesso():
    """
    Testa se o entrypoint principal (classificar_chamado) decodifica corretamente 
    o payload enviado em base64 pelo Pub/Sub e chama o orquestrador do caso de uso.
    """
    # 1. Payload simulado conforme o contrato contratos_payloads_spec
    payload_original = {
        "chamado_id": "test-integracao-uuid-1",
        "cliente_id": "cliente-integracao-id",
        "data_criacao": "2026-06-29T13:00:00Z",
        "assunto": "Pergunta de rotina",
        "mensagem": "Olá, qual o prazo de resposta da ouvidoria?"
    }
    
    # 2. Transforma o payload em bytes e codifica em base64 (assim como o GCP Pub/Sub faz)
    payload_json_bytes = json.dumps(payload_original).encode('utf-8')
    payload_base64 = base64.b64encode(payload_json_bytes).decode('utf-8')
    
    event = {
        "data": payload_base64
    }
    context = MagicMock() # Mock de metadados de contexto do trigger
    
    # 3. Patch do use_case global instanciado em main.py para interceptar a execução
    with patch("main.use_case") as mock_use_case:
        classificar_chamado(event, context)
        
        # Valida se o orquestrador do caso de uso foi acionado uma vez
        mock_use_case.executar.assert_called_once()
        
        # Recupera o chamado passado ao método executar
        chamado_recebido = mock_use_case.executar.call_args[0][0]
        
        # Valida as propriedades da entidade mapeada
        assert chamado_recebido.chamado_id == "test-integracao-uuid-1"
        assert chamado_recebido.cliente_id == "cliente-integracao-id"
        assert chamado_recebido.assunto == "Pergunta de rotina"
        assert chamado_recebido.mensagem == "Olá, qual o prazo de resposta da ouvidoria?"
