import logging
from google.cloud import firestore
from domain.entities import Auditoria
from domain.interfaces import FirestoreRepositoryInterface

logger = logging.getLogger(__name__)

class GcpFirestoreRepository(FirestoreRepositoryInterface):
    def __init__(self) -> None:
        # Inicializa o cliente NoSQL do Firestore
        self.db = firestore.Client()
        self.collection_name = "chamados_auditoria"

    def salvar_auditoria(self, auditoria: Auditoria) -> None:
        """Salva as informações completas da auditoria na coleção chamados_auditoria se ela não existir."""
        doc_ref = self.db.collection(self.collection_name).document(auditoria.auditoria_id)
        
        # Checagem de idempotência: evita sobrescrever auditorias que o analista humano já revisou
        doc = doc_ref.get()
        if doc.exists:
            logger.warning(f"Auditoria {auditoria.auditoria_id} já existe no Firestore. Ignorando gravação para evitar sobrescrita de status.")
            return

        data = {
            "auditoria_id": auditoria.auditoria_id,
            "data_desvio": auditoria.data_desvio,
            "status_revisao": auditoria.status_revisao,
            "motivo_desvio": auditoria.motivo_desvio,
            "detalhes_seguranca": {
                "gatilhos_encontrados": auditoria.detalhes_seguranca.gatilhos_encontrados,
                "confianca_agente": auditoria.detalhes_seguranca.confianca_agente
            },
            "dados_originais": {
                "chamado_id": auditoria.dados_originais.chamado_id,
                "cliente_id": auditoria.dados_originais.cliente_id,
                "data_criacao": auditoria.dados_originais.data_criacao,
                "assunto": auditoria.dados_originais.assunto,
                "mensagem": auditoria.dados_originais.mensagem
            }
        }
        
        logger.info(f"Salvando auditoria {auditoria.auditoria_id} no Firestore.")
        doc_ref.set(data)
        logger.info("Documento persistido com sucesso no Firestore.")


