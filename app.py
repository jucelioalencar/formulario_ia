from flask import Flask, request, jsonify, render_template
import json
import os
from datetime import datetime

app = Flask(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

ARQUIVO_DADOS = os.path.join(DATA_DIR, 'formularios.json')

@app.route('/')
def index():
    return render_template('formulario.html')

@app.route('/formulario.html')
def formulario_legacy():
    return render_template('formulario.html')

@app.route('/salvar', methods=['POST'])
def salvar():
    dados = request.get_json()
    
    nome = dados.get('nome', '').strip()
    email = dados.get('email', '').strip()
    data_nascimento = dados.get('data-nascimento', '').strip()
    telefone = dados.get('telefone', '').strip()
    
    if not nome or not email or not data_nascimento or not telefone:
        return jsonify({'erro': 'Todos os campos são obrigatórios'}), 400
    
    data_formatada = data_nascimento
    try:
        datetime.strptime(data_formatada, '%d/%m/%Y')
    except ValueError:
        return jsonify({'erro': 'Data inválida. Use o formato DD/MM/YYYY'}), 400
    
    formulario = {
        'nome': nome,
        'email': email,
        'data_nascimento': data_formatada,
        'telefone': telefone,
        'data_cadastro': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    }
    
    formularios = []
    if os.path.exists(ARQUIVO_DADOS):
        with open(ARQUIVO_DADOS, 'r', encoding='utf-8') as f:
            try:
                formularios = json.load(f)
            except json.JSONDecodeError:
                formularios = []
    
    formularios.append(formulario)
    
    with open(ARQUIVO_DADOS, 'w', encoding='utf-8') as f:
        json.dump(formularios, f, ensure_ascii=False, indent=2)
    
    return jsonify({'mensagem': 'Formulário salvo com sucesso!'})

if __name__ == '__main__':
    app.run(debug=True)