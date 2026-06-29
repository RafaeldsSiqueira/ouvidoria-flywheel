import uuid
from datetime import datetime, timezone
from domain.entities import (
    Chamado,
    ChamadoResolvido,
    Auditoria,
    DetalhesSeguranca
)
from domain.rules import DetectorDeRisco
from domain.interfaces import (
    PubSubPublisherInterface,
    FirestoreRepositoryInterface,
    GeminiClassifierInterface
)

class ProcessarChamadoUseCase:
    def __init__(
        self,
        publisher: PubSubPublisherInterface,
        repository: FirestoreRepositoryInterface,
        classifier: GeminiClassifierInterface
    ) -> None:
        self.publisher = publisher
        self.repository = repository
        self.classifier = classifier

    def executar(self, chamado: Chamado) -> None:
        """
        Executa o fluxo de triagem do chamado.
        Se risco for detectado, desvia para auditoria. Caso contrário, classifica e resolve.
        """
        gatilhos = DetectorDeRisco.avaliar_risco(chamado)
        
        if gatilhos:
            # Cenário B: Risco Detectado (Desvio para Auditoria)
            auditoria = Auditoria(
                auditoria_id=str(uuid.uuid4()),
                data_desvio=datetime.now(timezone.utc).isoformat(),
                status_revisao="AGUARDANDO_HUMANO",
                motivo_desvio="RISCO_JURIDICO_DETECTADO",
                detalhes_seguranca=DetalhesSeguranca(
                    gatilhos_encontrados=gatilhos,
                    confianca_agente=1.0  # Regra determinística possui 100% de confiança
                ),
                dados_originais=chamado
            )
            self.publisher.publicar_auditoria(auditoria)
        else:
            # Cenário A: Sem Risco (Aprovação e Classificação por IA)
            analise_ia = self.classifier.classificar_chamado(chamado)
            
            chamado_resolvido = ChamadoResolvido(
                chamado_id=chamado.chamado_id,
                cliente_id=chamado.cliente_id,
                data_criacao=chamado.data_criacao,
                assunto=chamado.assunto,
                mensagem=chamado.mensagem,
                analise_ia=analise_ia,
                status_final="RESOLVED_AUTO",
                data_resolucao=datetime.now(timezone.utc).isoformat()
            )
            self.repository.salvar_chamado_resolvido(chamado_resolvido)
