import os
import json
import logging
import vertexai
from vertexai.generative_models import GenerativeModel
from domain.entities import Chamado, AnaliseIA
from domain.interfaces import GeminiClassifierInterface

logger = logging.getLogger(__name__)

class GeminiClassifierClient(GeminiClassifierInterface):
    def __init__(self) -> None:
        # Em Cloud Functions, o ID do projeto é definido automaticamente no ambiente pela GCP
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
        # Fallback para execução local/testes
        if not project_id:
            project_id = "project-647ad0dc-ac55-4368-859"
        
        location = "us-central1"
        logger.info(f"Inicializando Vertex AI no projeto {project_id} na regiao {location}.")
        vertexai.init(project=project_id, location=location)
        # Inicializa o modelo do Gemini via Vertex AI com versão estável
        self.model = GenerativeModel("gemini-1.5-flash-001")

    def classificar_chamado(self, chamado: Chamado) -> AnaliseIA:
        """Envia o chamado para a API da Vertex AI e obtém a classificação estruturada em JSON."""
        logger.info(f"Enviando chamado {chamado.chamado_id} para classificação via Vertex AI.")
        
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
            logger.error(f"Erro ao consultar ou parsear a classificação do Gemini na Vertex AI: {e}")
            # Em caso de erro na chamada da IA, recorre a um fallback padrão para resiliência do sistema
            return AnaliseIA(
                classificacao_sugerida="DUVIDA",
                confianca_agente=0.0,
                motivo=f"Fallback acionado devido a falha técnica na Vertex AI: {str(e)}"
            )
