# Formulário IA

Sistema de formulário web com Flask.

## Link de Produção

https://formulario-ia-51y4.onrender.com

## Como Executar Localmente

### Pré-requisitos

- Python 3.10+

### Instalação

```bash
pip install -r requirements.txt
```

### Executar com Flask (desenvolvimento)

```bash
python app.py
```

Acesse: http://127.0.0.1:5000

### Executar com Gunicorn (produção)

```bash
gunicorn -w 2 -b 0.0.0.0:8000 app:app
```

Acesse: http://127.0.0.1:8000

## Testes

```bash
pytest
```