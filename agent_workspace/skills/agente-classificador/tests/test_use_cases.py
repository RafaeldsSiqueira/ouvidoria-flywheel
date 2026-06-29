from domain.entities import Chamado
from use_cases.classificar import ProcessarChamadoUseCase

def test_cenario_a_aprovacao_sem_risco(fake_publisher, fake_repository, fake_classifier):
    # Inicializa o caso de uso com os fakes injetados
    use_case = ProcessarChamadoUseCase(
        publisher=fake_publisher,
        repository=fake_repository,
        classifier=fake_classifier
    )
    
    chamado = Chamado(
        chamado_id="uuid_resolvido",
        cliente_id="cliente_1",
        data_criacao="2026-06-29T12:00:00Z",
        assunto="Parabéns pelo ótimo atendimento",
        mensagem="Fui muito bem atendido pelo suporte telefônico."
    )
    
    # Define o comportamento simulado do classificador do Gemini
    fake_classifier.classificacao_sugerida = "ELOGIO"
    fake_classifier.confianca_agente = 0.98
    fake_classifier.motivo = "O cliente expressa gratidão e elogia o suporte."

    # Executa a regra
    use_case.executar(chamado)
    
    # Validações Cenário A:
    # 1. Deve ser salvo na coleção 'chamados_resolvidos'
    assert chamado.chamado_id in fake_repository.chamados_resolvidos
    chamado_salvo = fake_repository.chamados_resolvidos[chamado.chamado_id]
    
    assert chamado_salvo.status_final == "RESOLVED_AUTO"
    assert chamado_salvo.analise_ia.classificacao_sugerida == "ELOGIO"
    assert chamado_salvo.analise_ia.confianca_agente == 0.98
    assert chamado_salvo.data_resolucao is not None
    
    # 2. Não deve publicar nenhuma mensagem de auditoria
    assert len(fake_publisher.mensagens_publicadas) == 0

def test_cenario_b_bloqueio_com_risco_juridico(fake_publisher, fake_repository, fake_classifier):
    use_case = ProcessarChamadoUseCase(
        publisher=fake_publisher,
        repository=fake_repository,
        classifier=fake_classifier
    )
    
    chamado = Chamado(
        chamado_id="uuid_auditoria",
        cliente_id="cliente_2",
        data_criacao="2026-06-29T12:00:00Z",
        assunto="Cobrança indevida, vou ao PROCON",
        mensagem="Não reconheço essa assinatura."
    )
    
    # Executa a regra
    use_case.executar(chamado)
    
    # Validações Cenário B:
    # 1. Não deve salvar na coleção 'chamados_resolvidos'
    assert chamado.chamado_id not in fake_repository.chamados_resolvidos
    
    # 2. Deve publicar no tópico de auditoria do Pub/Sub
    assert len(fake_publisher.mensagens_publicadas) == 1
    auditoria_publicada = fake_publisher.mensagens_publicadas[0]
    
    assert auditoria_publicada.status_revisao == "AGUARDANDO_HUMANO"
    assert auditoria_publicada.motivo_desvio == "RISCO_JURIDICO_DETECTADO"
    assert "procon" in auditoria_publicada.detalhes_seguranca.gatilhos_encontrados
    assert auditoria_publicada.dados_originais.chamado_id == chamado.chamado_id
