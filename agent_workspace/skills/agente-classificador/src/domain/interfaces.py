from abc import ABC, abstractmethod
from domain.entities import Chamado, ChamadoResolvido, Auditoria, AnaliseIA

class PubSubPublisherInterface(ABC):
    @abstractmethod
    def publicar_auditoria(self, auditoria: Auditoria) -> None:
        """Publica um chamado desviado para auditoria no tópico correspondente."""
        pass

class FirestoreRepositoryInterface(ABC):
    @abstractmethod
    def salvar_chamado_resolvido(self, chamado: ChamadoResolvido) -> None:
        """Salva o chamado resolvido na coleção correspondente do Firestore."""
        pass

class GeminiClassifierInterface(ABC):
    @abstractmethod
    def classificar_chamado(self, chamado: Chamado) -> AnaliseIA:
        """Interage com a IA do Gemini para classificar a categoria do chamado."""
        pass
