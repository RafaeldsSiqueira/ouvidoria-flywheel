import sys
import os
import pytest

# Adiciona o diretório 'src' ao sys.path para garantir que as importações absolutas (domain, use_cases, etc.) funcionem nos testes locais
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from domain.entities import Chamado, ChamadoResolvido, Auditoria, AnaliseIA
from domain.interfaces import (
    PubSubPublisherInterface,
    FirestoreRepositoryInterface,
    GeminiClassifierInterface
)

class FakePubSubPublisher(PubSubPublisherInterface):
    def __init__(self) -> None:
        self.mensagens_publicadas = []

    def publicar_auditoria(self, auditoria: Auditoria) -> None:
        self.mensagens_publicadas.append(auditoria)

class FakeFirestoreRepository(FirestoreRepositoryInterface):
    def __init__(self) -> None:
        self.chamados_resolvidos = {}

    def salvar_chamado_resolvido(self, chamado: ChamadoResolvido) -> None:
        self.chamados_resolvidos[chamado.chamado_id] = chamado

class FakeGeminiClassifier(GeminiClassifierInterface):
    def __init__(self) -> None:
        self.classificacao_sugerida = "DUVIDA"
        self.confianca_agente = 0.85
        self.motivo = "Mock de classificação do Gemini."

    def classificar_chamado(self, chamado: Chamado) -> AnaliseIA:
        return AnaliseIA(
            classificacao_sugerida=self.classificacao_sugerida,
            confianca_agente=self.confianca_agente,
            motivo=self.motivo
        )

@pytest.fixture
def fake_publisher() -> FakePubSubPublisher:
    return FakePubSubPublisher()

@pytest.fixture
def fake_repository() -> FakeFirestoreRepository:
    return FakeFirestoreRepository()

@pytest.fixture
def fake_classifier() -> FakeGeminiClassifier:
    return FakeGeminiClassifier()
