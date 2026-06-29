import base64
import json
import logging
from domain.entities import Auditoria, ChamadoOriginal, DetalhesSeguranca
from use_cases.processar import ProcessarAuditoriaUseCase
from infrastructure.firestore_client import GcpFirestoreRepository

# Configuração de logs estruturados em conformidade com o padrão do projeto
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# Instanciação global do repositório NoSQL Firestore e caso de uso correspondente
try:
    repository = GcpFirestoreRepository()
    use_case = ProcessarAuditoriaUseCase(repository=repository)
except Exception as e:
    logger.error(f"Erro ao inicializar dependências do Firestore no cold-start da auditoria: {e}")
    use_case = None

def processar_auditoria(event, context):
    """
    Handler principal da Cloud Function processa-auditoria.
    Ativado por mensagens publicadas no topico-auditoria do Pub/Sub.
    """
    logger.info("Executando a Cloud Function processar_auditoria.")
    
    if use_case is None:
        logger.critical("O Caso de Uso de auditoria não foi inicializado corretamente devido a problemas de infraestrutura.")
        raise RuntimeError("Inicialização falhou.")

    try:
        # 1. Verificação e decodificação do evento vindo do Pub/Sub
        if 'data' not in event:
            logger.error("Evento Pub/Sub recebido sem campo de dados 'data'.")
            return

        payload_decoded = base64.b64decode(event['data']).decode('utf-8')
        data = json.loads(payload_decoded)

        # 2. Mapeamento das estruturas do JSON para entidades do domínio
        dados_originais_dict = data['dados_originais']
        chamado_original = ChamadoOriginal(
            chamado_id=dados_originais_dict['chamado_id'],
            cliente_id=dados_originais_dict['cliente_id'],
            data_criacao=dados_originais_dict['data_criacao'],
            assunto=dados_originais_dict['assunto'],
            mensagem=dados_originais_dict['mensagem']
        )
        
        detalhes_seguranca_dict = data['detalhes_seguranca']
        detalhes_seguranca = DetalhesSeguranca(
            gatilhos_encontrados=detalhes_seguranca_dict['gatilhos_encontrados'],
            confianca_agente=float(detalhes_seguranca_dict['confianca_agente'])
        )
        
        auditoria = Auditoria(
            auditoria_id=data['auditoria_id'],
            data_desvio=data['data_desvio'],
            status_revisao=data['status_revisao'],
            motivo_desvio=data['motivo_desvio'],
            detalhes_seguranca=detalhes_seguranca,
            dados_originais=chamado_original
        )
        
        logger.info(f"Gravando auditoria para o chamado {chamado_original.chamado_id} no banco de dados.")

        # 3. Execução do caso de uso
        use_case.executar(auditoria)
        
        logger.info(f"Auditoria {auditoria.auditoria_id} persistida com sucesso no Firestore.")

    except KeyError as ke:
        logger.error(f"Erro de validação contratual do payload recebido: chave ausente {ke}")
    except json.JSONDecodeError as jde:
        logger.error(f"Mensagem em formato JSON corrompido ou inválido recebida no Pub/Sub: {jde}")
    except Exception as e:
        logger.error(f"Exceção não tratada na execução da Cloud Function de auditoria: {e}")
        raise e
