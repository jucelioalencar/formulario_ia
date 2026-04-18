@echo off
echo Instalando dependencias de teste...
pip install -r requirements.txt

echo.
echo Rodando testes...
python -m pytest test_app.py -v

echo.
pause