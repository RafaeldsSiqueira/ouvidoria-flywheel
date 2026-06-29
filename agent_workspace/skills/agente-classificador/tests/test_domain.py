from domain.entities import Chamado
from domain.rules import DetectorDeRisco

def test_deve_retornar_sem_risco_quando_chamado_nao_contem_gatilhos():
    chamado = Chamado(
        chamado_id="123",
        cliente_id="cli_abc",
        data_criacao="2026-06-29T12:00:00Z",
        assunto="Dúvida de Acesso",
        mensagem="Olá, não estou conseguindo fazer login no portal da ouvidoria. Podem ajudar?"
    )
    
    gatilhos = DetectorDeRisco.avaliar_risco(chamado)
    
    assert len(gatilhos) == 0
    assert not gatilhos

def test_deve_detectar_risco_quando_assunto_contem_termo_critico():
    chamado = Chamado(
        chamado_id="123",
        cliente_id="cli_abc",
        data_criacao="2026-06-29T12:00:00Z",
        assunto="Vou entrar com processo no PROCON",
        mensagem="Entrei em contato anteriormente e nada foi feito."
    )
    
    gatilhos = DetectorDeRisco.avaliar_risco(chamado)
    
    assert "procon" in gatilhos
    assert "processo" in gatilhos
    assert len(gatilhos) == 2

def test_deve_detectar_risco_quando_mensagem_contem_termo_critico_case_insensitive():
    chamado = Chamado(
        chamado_id="123",
        cliente_id="cli_abc",
        data_criacao="2026-06-29T12:00:00Z",
        assunto="Reclamação de cobrança",
        mensagem="Se não cancelarem a taxa indevida, falarei com meu ADVOGADO para me defender judicialmente."
    )
    
    gatilhos = DetectorDeRisco.avaliar_risco(chamado)
    
    assert "advogado" in gatilhos
    assert "judicial" in gatilhos
    assert len(gatilhos) == 2
