from dataclasses import dataclass
from typing import List, Optional

@dataclass(frozen=True)
class Chamado:
    chamado_id: str
    cliente_id: str
    data_criacao: str
    assunto: str
    mensagem: str

@dataclass(frozen=True)
class AnaliseIA:
    classificacao_sugerida: str
    confianca_agente: float
    motivo: str

@dataclass(frozen=True)
class ChamadoResolvido:
    chamado_id: str
    cliente_id: str
    data_criacao: str
    assunto: str
    mensagem: str
    analise_ia: AnaliseIA
    status_final: str
    data_resolucao: str

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
    dados_originais: Chamado
