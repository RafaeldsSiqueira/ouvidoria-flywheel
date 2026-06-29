import sys
import os
import pytest

# Adiciona o diretório 'src' ao sys.path para garantir que as importações absolutas (domain, use_cases, etc.) funcionem nos testes locais do processa-auditoria
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from domain.entities import Auditoria
from domain.interfaces import FirestoreRepositoryInterface

class FakeFirestoreRepository(FirestoreRepositoryInterface):
    def __init__(self) -> None:
        self.db = {}

    def salvar_auditoria(self, auditoria: Auditoria) -> None:
        """Mock de persistência NoSQL que grava a entidade em dicionário em memória."""
        self.db[auditoria.auditoria_id] = auditoria

@pytest.fixture
def fake_repository() -> FakeFirestoreRepository:
    return FakeFirestoreRepository()
