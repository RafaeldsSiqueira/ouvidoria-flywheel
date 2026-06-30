import pytest
from use_cases.finalizar import FinalizarAuditoria

def test_finalizar_auditoria_sucesso(fake_repository):
    chamado_id = "11111111-1111-1111-1111-111111111111"
    use_case = FinalizarAuditoria(fake_repository)
    
    resultado = use_case.execute(
        chamado_id=chamado_id,
        analista="analista-silva",
        acao="APROVADO",
        classificacao_final="DUVIDA"
    )
    
    assert resultado is True
    # Verifica que o status foi atualizado para RESOLVIDO
    assert fake_repository.auditorias_db[chamado_id]["status_revisao"] == "RESOLVIDO"
    assert fake_repository.auditorias_db[chamado_id]["data_resolucao"] is not None
    
    # Verifica que o log de treinamento foi salvo
    assert len(fake_repository.logs_db) == 1
    log = list(fake_repository.logs_db.values())[0]
    assert log.chamado_id == chamado_id
    assert log.analista_responsavel == "analista-silva"
    assert log.decisao_humana.acao == "APROVADO"
    assert log.decisao_humana.classificacao_final == "DUVIDA"

def test_finalizar_auditoria_nao_encontrado(fake_repository):
    use_case = FinalizarAuditoria(fake_repository)
    resultado = use_case.execute(
        chamado_id="nao-existente",
        analista="analista-silva",
        acao="CORRIGIDO",
        classificacao_final="RECLAMACAO"
    )
    assert resultado is False
    assert len(fake_repository.logs_db) == 0

def test_finalizar_auditoria_acao_invalida(fake_repository):
    use_case = FinalizarAuditoria(fake_repository)
    with pytest.raises(ValueError, match="Ação inválida"):
        use_case.execute(
            chamado_id="11111111-1111-1111-1111-111111111111",
            analista="analista-silva",
            acao="ACAO_INVALIDA",
            classificacao_final="DUVIDA"
        )

def test_finalizar_auditoria_categoria_invalida(fake_repository):
    use_case = FinalizarAuditoria(fake_repository)
    with pytest.raises(ValueError, match="Classificação final inválida"):
        use_case.execute(
            chamado_id="11111111-1111-1111-1111-111111111111",
            analista="analista-silva",
            acao="APROVADO",
            classificacao_final="CATEGORIA_INVALIDA"
        )
