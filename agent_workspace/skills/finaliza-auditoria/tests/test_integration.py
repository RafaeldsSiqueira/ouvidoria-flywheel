import pytest
from unittest.mock import MagicMock
from flask import Flask, request
from main import webhook_resolucao

def test_webhook_resolucao_sucesso(mocker):
    # Mock do caso de uso global do main.py
    mock_use_case = MagicMock()
    mock_use_case.execute.return_value = True
    mocker.patch('main.use_case', mock_use_case)

    # Cria app Flask temporário para gerar o contexto de request
    app = Flask(__name__)
    with app.test_request_context(
        json={
            "chamado_id": "11111111-1111-1111-1111-111111111111",
            "analista_responsavel": "analista-silva",
            "decisao_humana": {
                "acao": "APROVADO",
                "classificacao_final": "DUVIDA"
            }
        },
        method="POST"
    ):
        response, status_code = webhook_resolucao(request)
        
        assert status_code == 200
        assert response.json["status"] == "RESOLVIDO"
        assert response.json["message"] == "Resolution registered successfully."
        mock_use_case.execute.assert_called_once_with(
            chamado_id="11111111-1111-1111-1111-111111111111",
            analista="analista-silva",
            acao="APROVADO",
            classificacao_final="DUVIDA"
        )

def test_webhook_resolucao_campos_ausentes(mocker):
    mock_use_case = MagicMock()
    mocker.patch('main.use_case', mock_use_case)

    app = Flask(__name__)
    with app.test_request_context(
        json={
            "chamado_id": "11111111-1111-1111-1111-111111111111"
            # Faltam analista_responsavel e decisao_humana
        },
        method="POST"
    ):
        response, status_code = webhook_resolucao(request)
        
        assert status_code == 400
        assert "Missing required fields" in response.json["error"]
        mock_use_case.execute.assert_not_called()

def test_webhook_resolucao_metodo_incorreto(mocker):
    mock_use_case = MagicMock()
    mocker.patch('main.use_case', mock_use_case)

    app = Flask(__name__)
    with app.test_request_context(method="GET"):
        response, status_code = webhook_resolucao(request)
        
        assert status_code == 405
        assert "Method Not Allowed" in response.json["error"]
        mock_use_case.execute.assert_not_called()

def test_webhook_resolucao_nao_encontrado(mocker):
    mock_use_case = MagicMock()
    mock_use_case.execute.return_value = False
    mocker.patch('main.use_case', mock_use_case)

    app = Flask(__name__)
    with app.test_request_context(
        json={
            "chamado_id": "nao-existente",
            "analista_responsavel": "analista-silva",
            "decisao_humana": {
                "acao": "CORRIGIDO",
                "classificacao_final": "RECLAMACAO"
            }
        },
        method="POST"
    ):
        response, status_code = webhook_resolucao(request)
        
        assert status_code == 404
        assert "not found in audit queue" in response.json["error"]
