from typing import List
from domain.entities import Chamado

class DetectorDeRisco:
    GATILHOS = [
        "processo",
        "procon",
        "advogado",
        "justiça",
        "judicial",
        "intimação",
        "processar",
        "danos morais"
    ]

    @classmethod
    def avaliar_risco(cls, chamado: Chamado) -> List[str]:
        """
        Avalia se o assunto ou a mensagem do chamado contêm termos críticos de risco.
        Retorna uma lista contendo os termos de risco encontrados.
        """
        gatilhos_encontrados = []
        texto_analise = f"{chamado.assunto} {chamado.mensagem}".lower()
        
        for gatilho in cls.GATILHOS:
            if gatilho in texto_analise:
                gatilhos_encontrados.append(gatilho)
                
        return gatilhos_encontrados
