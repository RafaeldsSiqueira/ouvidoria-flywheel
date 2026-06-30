import os
import json
import logging
import google.generativeai as genai
from domain.entities import Chamado, AnaliseIA
from domain.interfaces import GeminiClassifierInterface

logger = logging.getLogger(__name__)

class GeminiClassifierClient(GeminiClassifierInterface):
    def __init__(self) -> None:
        # A chave de API do AI Studio é injetada automaticamente no ambiente a partir do Secret Manager
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            logger.warning("Variável GEMINI_API_KEY não encontrada no ambiente. Certifique-se de configurar o Secret Manager.")
        else:
            logger.info("Inicializando Gemini API Client via Google AI Studio.")
            genai.configure(api_key=api_key)
        
        # Inicializa o modelo usando o SDK público do AI Studio com alias dinâmico/mais recente
        self.model = genai.GenerativeModel("gemini-flash-latest")

    def classificar_chamado(self, chamado: Chamado) -> AnaliseIA:
        """Envia o chamado para a API do Gemini e obtém a classificação estruturada em JSON."""
        logger.info(f"Enviando chamado {chamado.chamado_id} para classificação via Google AI Studio.")
        
        prompt = f"""
        Você é um triador inteligente de chamados de ouvidoria de clientes.
        Com base no assunto e na mensagem a seguir, classifique o chamado em uma das quatro categorias:
        - DUVIDA
        - RECLAMACAO
        - ELOGIO
        - SUGESTAO

        Responda estritamente sob o formato JSON abaixo, sem formatações adicionais ou marcações de markdown:
        {{
            "classificacao_sugerida": "DUVIDA | RECLAMACAO | ELOGIO | SUGESTAO",
            "confianca_agente": 0.0 a 1.0,
            "motivo": "Uma explicação de uma frase do porquê desta classificação"
        }}

        Chamado:
        Assunto: {chamado.assunto}
        Mensagem: {chamado.mensagem}
        """
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            
            # Decodifica a resposta JSON
            res_json = json.loads(response.text)
            
            return AnaliseIA(
                classificacao_sugerida=res_json.get("classificacao_sugerida", "DUVIDA").strip().upper(),
                confianca_agente=float(res_json.get("confianca_agente", 0.5)),
                motivo=res_json.get("motivo", "Sem justificativa fornecida.")
            )
            
        except Exception as e:
            logger.error(f"Erro ao consultar ou parsear a classificação do Gemini: {e}")
            # Em caso de erro, recorre ao fallback para manter a resiliência do sistema
            return AnaliseIA(
                classificacao_sugerida="DUVIDA",
                confianca_agente=0.0,
                motivo=f"Fallback acionado devido a falha técnica: {str(e)}"
            )
