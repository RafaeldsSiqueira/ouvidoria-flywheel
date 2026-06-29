import json
import os
import logging
from google.cloud import pubsub_v1
from domain.entities import Auditoria
from domain.interfaces import PubSubPublisherInterface

logger = logging.getLogger(__name__)

class GcpPubSubPublisher(PubSubPublisherInterface):
    def __init__(self) -> None:
        self.publisher = pubsub_v1.PublisherClient()
        self.project_id = os.environ.get("GCP_PROJECT_ID")
        self.topic_id = "topico-auditoria"
        self.topic_path = self.publisher.topic_path(self.project_id, self.topic_id)

    def publicar_auditoria(self, auditoria: Auditoria) -> None:
        """Publica a auditoria no Pub/Sub no tópico topico-auditoria."""
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
        
        payload_bytes = json.dumps(data).encode("utf-8")
        logger.info(f"Publicando auditoria para o chamado {auditoria.dados_originais.chamado_id} no Pub/Sub.")
        
        future = self.publisher.publish(self.topic_path, payload_bytes)
        # Bloqueia a execução até que a publicação seja confirmada (ou gere exceção)
        message_id = future.result()
        logger.info(f"Mensagem de auditoria publicada com sucesso. ID: {message_id}")
