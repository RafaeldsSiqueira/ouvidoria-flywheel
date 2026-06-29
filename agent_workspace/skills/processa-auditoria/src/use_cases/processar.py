from domain.entities import Auditoria
from domain.interfaces import FirestoreRepositoryInterface

class ProcessarAuditoriaUseCase:
    def __init__(self, repository: FirestoreRepositoryInterface) -> None:
        self.repository = repository

    def executar(self, auditoria: Auditoria) -> None:
        """
        Caso de uso para processamento e desvio.
        Persiste os dados de auditoria no banco NoSQL.
        """
        self.repository.salvar_auditoria(auditoria)
