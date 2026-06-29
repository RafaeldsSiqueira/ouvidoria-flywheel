from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class ChamadoOriginal:
    chamado_id: str
    cliente_id: str
    data_criacao: str
    assunto: str
    mensagem: str

@dataclass(frozen=True)
class DetalhesSeguranca:
    gatilhos_encontrados: List[str]
    confianca_agente: float

@dataclass(frozen=True)
class Auditoria:
    auditoria_id: str
    data_desvio: str
    status_revisao: str
    motivo_desvio: str
    detalhes_seguranca: DetalhesSeguranca
    dados_originais: ChamadoOriginal
