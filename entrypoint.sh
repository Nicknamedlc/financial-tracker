#!/bin/sh

# Executa as migrações do banco de dados
#poetry run alembic revision --autogenerate -m "Criação das tabelas"

poetry run alembic upgrade head
# Inicia a aplicação
poetry run uvicorn --host 127.0.0.1 --port 8000 src.app.main:app