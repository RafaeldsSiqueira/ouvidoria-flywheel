from abc import ABC, abstractmethod
from domain.entities import LogTreinamento

class FirestoreRepositoryInterface(ABC):
    @abstractmethod
    def update_auditoria_status(self, chamado_id: str, status: str, data_resolucao: str) -> bool:
        """Atualiza o status de um chamado na coleção chamados_auditoria para RESOLVIDO."""
        pass

    @abstractmethod
    def save_log_treinamento(self, log: LogTreinamento) -> None:
        """Salva o log de treinamento na coleção logs_treinamento para o Data Flywheel."""
        pass
