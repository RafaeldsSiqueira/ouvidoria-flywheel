import logging
import functions_framework
from flask import Request, jsonify
from infrastructure.firestore_client import GcpFirestoreRepository
from use_cases.finalizar import FinalizarAuditoria

# Configuração básica de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Instancia o repositório e o caso de uso globalmente para cache de instâncias (Warm Starts)
repo = GcpFirestoreRepository()
use_case = FinalizarAuditoria(repo)

@functions_framework.http
def webhook_resolucao(request: Request):
    """Webhook HTTP acionado pelo CRM ou Painel GCP para registrar a resolução e o log de treinamento."""
    # Permite apenas chamadas POST
    if request.method != "POST":
        return jsonify({"error": "Method Not Allowed. Use POST."}), 405

    try:
        request_json = request.get_json(silent=True)
        if not request_json:
            return jsonify({"error": "Bad Request. JSON body is required."}), 400

        # Extração de parâmetros obrigatórios do payload
        chamado_id = request_json.get("chamado_id")
        analista = request_json.get("analista_responsavel")
        decisao = request_json.get("decisao_humana", {})
        acao = decisao.get("acao")
        classificacao_final = decisao.get("classificacao_final")

        if not all([chamado_id, analista, acao, classificacao_final]):
            return jsonify({
                "error": "Missing required fields: chamado_id, analista_responsavel, decisao_humana.acao, decisao_humana.classificacao_final"
            }), 400

        # Execução do Caso de Uso
        logger.info(f"Recebido evento de resolução para o chamado {chamado_id}.")
        sucesso = use_case.execute(
            chamado_id=chamado_id,
            analista=analista,
            acao=acao,
            classificacao_final=classificacao_final
        )

        if not sucesso:
            return jsonify({"error": f"Ticket {chamado_id} not found in audit queue."}), 404

        return jsonify({
            "message": "Resolution registered successfully.",
            "chamado_id": chamado_id,
            "status": "RESOLVIDO"
        }), 200

    except ValueError as e:
        logger.error(f"Erro de validação: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Erro inesperado no webhook de resolução: {str(e)}")
        return jsonify({"error": "Internal Server Error."}), 500
