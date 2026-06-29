import logging
from google.cloud import firestore
from domain.entities import ChamadoResolvido
from domain.interfaces import FirestoreRepositoryInterface

logger = logging.getLogger(__name__)

class GcpFirestoreRepository(FirestoreRepositoryInterface):
    def __init__(self) -> None:
        # Inicializa o cliente do Firestore usando as credenciais padrão do ambiente
        self.db = firestore.Client()
        self.collection_name = "chamados_resolvidos"

    def salvar_chamado_resolvido(self, chamado: ChamadoResolvido) -> None:
        """Persiste o chamado resolvido automaticamente na coleção chamados_resolvidos."""
        doc_ref = self.db.collection(self.collection_name).document(chamado.chamado_id)
        
        data = {
            "chamado_id": chamado.chamado_id,
            "cliente_id": chamado.cliente_id,
            "data_criacao": chamado.data_criacao,
            "assunto": chamado.assunto,
            "mensagem": chamado.mensagem,
            "analise_ia": {
                "classificacao_sugerida": chamado.analise_ia.classificacao_sugerida,
                "confianca_agente": chamado.analise_ia.confianca_agente,
                "motivo": chamado.analise_ia.motivo
            },
            "status_final": chamado.status_final,
            "data_resolucao": chamado.data_resolucao
        }
        
        logger.info(f"Salvando documento de chamado resolvido {chamado.chamado_id} no Firestore.")
        doc_ref.set(data)
        logger.info("Documento salvo com sucesso no Firestore.")
