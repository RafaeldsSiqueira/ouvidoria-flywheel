from abc import ABC, abstractmethod
from domain.entities import Auditoria

class FirestoreRepositoryInterface(ABC):
    @abstractmethod
    def salvar_auditoria(self, auditoria: Auditoria) -> None:
        """Interface (porta) para gravação do chamado de auditoria no Firestore."""
        pass
