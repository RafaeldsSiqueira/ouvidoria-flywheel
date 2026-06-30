import sys
import os
import pytest

# Adiciona o diretório 'src' ao sys.path para garantir que as importações absolutas funcionem nos testes locais
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from domain.interfaces import FirestoreRepositoryInterface
from domain.entities import LogTreinamento

class FakeFirestoreRepository(FirestoreRepositoryInterface):
    def __init__(self) -> None:
        # Banco NoSQL mockado em memória para os testes
        self.auditorias_db = {
            "11111111-1111-1111-1111-111111111111": {
                "status_revisao": "AGUARDANDO_HUMANO",
                "data_resolucao": None
            }
        }
        self.logs_db = {}

    def update_auditoria_status(self, chamado_id: str, status: str, data_resolucao: str) -> bool:
        if chamado_id not in self.auditorias_db:
            return False
        self.auditorias_db[chamado_id]["status_revisao"] = status
        self.auditorias_db[chamado_id]["data_resolucao"] = data_resolucao
        return True

    def save_log_treinamento(self, log: LogTreinamento) -> None:
        self.logs_db[log.log_id] = log

@pytest.fixture
def fake_repository() -> FakeFirestoreRepository:
    return FakeFirestoreRepository()
