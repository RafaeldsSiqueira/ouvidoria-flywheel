import logging
from google.cloud import firestore
from domain.entities import LogTreinamento
from domain.interfaces import FirestoreRepositoryInterface

logger = logging.getLogger(__name__)

class GcpFirestoreRepository(FirestoreRepositoryInterface):
    def __init__(self) -> None:
        self.db = firestore.Client()

    def update_auditoria_status(self, chamado_id: str, status: str, data_resolucao: str) -> bool:
        """Busca o chamado pelo chamado_id na fila de auditoria e atualiza seu status de revisão."""
        logger.info(f"Buscando chamado {chamado_id} na coleção chamados_auditoria...")
        
        # Realiza a query para encontrar o documento com o chamado_id correspondente
        query = self.db.collection("chamados_auditoria").where("dados_originais.chamado_id", "==", chamado_id).limit(1)
        docs = list(query.stream())
        
        if not docs:
            logger.warning(f"Chamado {chamado_id} não encontrado na fila de auditoria.")
            return False
            
        doc_ref = docs[0].reference
        logger.info(f"Atualizando chamado {chamado_id} para o status {status}...")
        doc_ref.update({
            "status_revisao": status,
            "data_resolucao": data_resolucao
        })
        logger.info("Status da auditoria atualizado com sucesso no Firestore.")
        return True

    def save_log_treinamento(self, log: LogTreinamento) -> None:
        """Salva o log do Data Flywheel na coleção logs_treinamento."""
        logger.info(f"Persistindo log de treinamento {log.log_id} para o chamado {log.chamado_id}...")
        doc_ref = self.db.collection("logs_treinamento").document(log.log_id)
        
        data = {
            "log_id": log.log_id,
            "chamado_id": log.chamado_id,
            "data_resolucao": log.data_resolucao,
            "analista_responsavel": log.analista_responsavel,
            "decisao_humana": {
                "acao": log.decisao_humana.acao,
                "classificacao_final": log.decisao_humana.classificacao_final
            }
        }
        
        doc_ref.set(data)
        logger.info("Log de treinamento salvo com sucesso no Firestore.")
