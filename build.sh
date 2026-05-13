#!/usr/bin/env bash
# Внутри build.sh вместо grep/xargs
set -a            # Включает режим автоматического экспорта всех новых переменных
source .env       # Читает файл .env
set +a            # Выключает режим
psql -d "$DATABASE_URL" -f init.sql