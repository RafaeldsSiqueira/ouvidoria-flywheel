import uuid
from datetime import datetime, timezone
from domain.entities import LogTreinamento, DecisaoHumana
from domain.interfaces import FirestoreRepositoryInterface

class FinalizarAuditoria:
    def __init__(self, repo: FirestoreRepositoryInterface):
        self.repo = repo

    def execute(self, chamado_id: str, analista: str, acao: str, classificacao_final: str) -> bool:
        # 1. Validações de Domínio
        if acao not in ["APROVADO", "CORRIGIDO"]:
            raise ValueError("Ação inválida. Deve ser APROVADO ou CORRIGIDO.")
        
        categorias_validas = ["DUVIDA", "RECLAMACAO", "ELOGIO", "SUGESTAO"]
        if classificacao_final not in categorias_validas:
            raise ValueError(f"Classificação final inválida. Deve ser uma de: {categorias_validas}")

        # 2. Obter carimbo de data/hora atual
        data_resolucao = datetime.now(timezone.utc).isoformat()

        # 3. Atualizar o status da auditoria no Firestore para RESOLVIDO
        status_atualizado = self.repo.update_auditoria_status(chamado_id, "RESOLVIDO", data_resolucao)
        if not status_atualizado:
            # Se o chamado não existir na fila de auditoria, ignora ou levanta erro
            return False

        # 4. Criar o Log de Treinamento (Data Flywheel)
        log_id = str(uuid.uuid4())
        decisao = DecisaoHumana(acao=acao, classificacao_final=classificacao_final)
        log = LogTreinamento(
            log_id=log_id,
            chamado_id=chamado_id,
            data_resolucao=data_resolucao,
            analista_responsavel=analista,
            decisao_humana=decisao
        )

        # 5. Salvar o log na coleção de treinamento
        self.repo.save_log_treinamento(log)
        return True
