from dataclasses import dataclass

@dataclass(frozen=True)
class DecisaoHumana:
    acao: str             # "APROVADO" ou "CORRIGIDO"
    classificacao_final: str # "DUVIDA", "RECLAMACAO", "ELOGIO", "SUGESTAO"

@dataclass(frozen=True)
class LogTreinamento:
    log_id: str
    chamado_id: str
    data_resolucao: str
    analista_responsavel: str
    decisao_humana: DecisaoHumana
