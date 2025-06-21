#!/bin/sh

# Executa as migrações do banco de dados
poetry run alembic revision --autogenerate -m "Criação das tabelas"
poetry run alembic upgrade head
# Inicia a aplicação
poetry run uvicorn --host 0.0.0.0 --port 8000 app.app:app