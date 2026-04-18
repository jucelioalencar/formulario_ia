import pytest
import json
import os
import sys
from app import app, ARQUIVO_DADOS

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def dados_teste():
    return {
        'nome': 'João Silva',
        'email': 'joao@email.com',
        'data-nascimento': '25/12/1990',
        'telefone': '(11) 99999-9999'
    }

class TestFormulario:
    def test_pagina_carrega(self, client):
        resposta = client.get('/')
        assert resposta.status_code == 200
        assert resposta.data.startswith(b'<!DOCTYPE html>')

    def test_salvar_formulario_sucesso(self, client, dados_teste):
        resposta = client.post('/salvar', 
                           data=json.dumps(dados_teste),
                           content_type='application/json')
        dados = json.loads(resposta.data)
        assert resposta.status_code == 200
        assert 'sucesso' in dados['mensagem'].lower()

    def test_salvar_campos_obrigatorios(self, client):
        dados_invalidos = {'nome': '', 'email': '', 'data-nascimento': '', 'telefone': ''}
        resposta = client.post('/salvar',
                             data=json.dumps(dados_invalidos),
                             content_type='application/json')
        dados = json.loads(resposta.data)
        assert resposta.status_code == 400
        assert 'obrigatórios' in dados['erro']

    def test_data_formato_invalido(self, client):
        dados_invalidos = {
            'nome': 'João Silva',
            'email': 'joao@email.com',
            'data-nascimento': '1990-25-12',
            'telefone': '(11) 99999-9999'
        }
        resposta = client.post('/salvar',
                             data=json.dumps(dados_invalidos),
                             content_type='application/json')
        dados = json.loads(resposta.data)
        assert resposta.status_code == 400
        assert 'inválida' in dados['erro']

    def test_dados_salvos_em_arquivo(self, client, dados_teste):
        if os.path.exists(ARQUIVO_DADOS):
            os.remove(ARQUIVO_DADOS)
        
        client.post('/salvar',
                  data=json.dumps(dados_teste),
                  content_type='application/json')
        
        assert os.path.exists(ARQUIVO_DADOS)
        with open(ARQUIVO_DADOS, 'r', encoding='utf-8') as f:
            formularios = json.load(f)
        assert len(formularios) > 0
        assert formularios[0]['nome'] == 'João Silva'

if __name__ == '__main__':
    pytest.main([__file__, '-v'])