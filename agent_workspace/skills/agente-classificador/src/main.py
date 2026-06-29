import base64
import json
import logging
from domain.entities import Chamado
from use_cases.classificar import ProcessarChamadoUseCase
from infrastructure.pubsub_client import GcpPubSubPublisher
from infrastructure.firestore_client import GcpFirestoreRepository
from infrastructure.gemini_client import GeminiClassifierClient

# Configuração estruturada de Logs (integração com GCP Cloud Logging)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# Instanciação dos adaptadores reais de infraestrutura de forma global
# As conexões serão inicializadas no cold start e reutilizadas nas execuções subsequentes
try:
    publisher = GcpPubSubPublisher()
    repository = GcpFirestoreRepository()
    classifier = GeminiClassifierClient()

    # Instanciação do Caso de Uso injetando os adaptadores
    use_case = ProcessarChamadoUseCase(
        publisher=publisher,
        repository=repository,
        classifier=classifier
    )
except Exception as e:
    logger.error(f"Erro ao inicializar adaptadores de infraestrutura durante o cold-start: {e}")
    # Definimos como None para tratar dinamicamente ou forçar falha no Handler
    use_case = None

def classificar_chamado(event, context):
    """
    Handler da Cloud Function disparado por eventos de mensagens Pub/Sub.
    Decodifica o payload JSON em base64 e delega a lógica de negócios para o caso de uso.
    """
    logger.info("Executando a Cloud Function classificar_chamado.")
    
    if use_case is None:
        logger.critical("O Caso de Uso não pôde ser inicializado devido a falhas na infraestrutura. Abortando execução.")
        raise RuntimeError("Inicialização falhou.")

    try:
        # 1. Obtenção do payload binário codificado em base64 do Pub/Sub
        if 'data' not in event:
            logger.error("Evento Pub/Sub inválido: campo 'data' ausente.")
            return

        payload_decoded = base64.b64decode(event['data']).decode('utf-8')
        data = json.loads(payload_decoded)

        # 2. Construção da Entidade de Domínio a partir do dicionário decodificado
        chamado = Chamado(
            chamado_id=data['chamado_id'],
            cliente_id=data['cliente_id'],
            data_criacao=data['data_criacao'],
            assunto=data['assunto'],
            mensagem=data['mensagem']
        )
        
        logger.info(f"Processando chamado ID: {chamado.chamado_id}")

        # 3. Execução do Caso de Uso
        use_case.executar(chamado)
        
        logger.info(f"Finalizado processamento com sucesso para o chamado {chamado.chamado_id}.")

    except KeyError as ke:
        logger.error(f"Erro de Validação de Contrato: chave ausente no payload {ke}")
    except json.JSONDecodeError as jde:
        logger.error(f"Erro de Deserialização JSON: dados corrompidos. {jde}")
    except Exception as e:
        logger.error(f"Erro crítico não tratado durante o processamento: {e}")
        # Lança a exceção para que o Pub/Sub possa retentar ou desviar para DLQ se configurado
        raise e
