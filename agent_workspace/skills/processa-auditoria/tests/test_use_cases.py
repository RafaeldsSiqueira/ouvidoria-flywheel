from domain.entities import Auditoria, ChamadoOriginal, DetalhesSeguranca
from use_cases.processar import ProcessarAuditoriaUseCase

def test_deve_gravar_auditoria_corretamente_no_repositorio(fake_repository):
    """
    Testa se o caso de uso ProcessarAuditoriaUseCase orquestra corretamente 
    a persistência do chamado de risco na camada de infraestrutura.
    """
    # Inicializa o caso de uso com o repositório mockado
    use_case = ProcessarAuditoriaUseCase(repository=fake_repository)
    
    chamado_original = ChamadoOriginal(
        chamado_id="chamado-uuid-99",
        cliente_id="cliente-uuid-88",
        data_criacao="2026-06-29T14:00:00Z",
        assunto="Abertura de Processo",
        mensagem="Encaminharei a petição ao juiz."
    )
    
    detalhes_seguranca = DetalhesSeguranca(
        gatilhos_encontrados=["processo"],
        confianca_agente=1.0
    )
    
    auditoria = Auditoria(
        auditoria_id="auditoria-uuid-77",
        data_desvio="2026-06-29T14:00:05Z",
        status_revisao="AGUARDANDO_HUMANO",
        motivo_desvio="RISCO_JURIDICO_DETECTADO",
        detalhes_seguranca=detalhes_seguranca,
        dados_originais=chamado_original
    )
    
    # Executa o caso de uso
    use_case.executar(auditoria)
    
    # Validações:
    # 1. O registro deve ser inserido no repositório Firestore sob o ID correto
    assert auditoria.auditoria_id in fake_repository.db
    
    # 2. As informações de dados e metadados devem permanecer idênticas e preservadas
    registro_salvo = fake_repository.db[auditoria.auditoria_id]
    assert registro_salvo.status_revisao == "AGUARDANDO_HUMANO"
    assert registro_salvo.motivo_desvio == "RISCO_JURIDICO_DETECTADO"
    assert registro_salvo.dados_originais.chamado_id == "chamado-uuid-99"
    assert "processo" in registro_salvo.detalhes_seguranca.gatilhos_encontrados
