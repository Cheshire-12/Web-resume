#!/usr/bin/env bash
# Внутри build.sh вместо grep/xargs
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
psql -d "$DATABASE_URL" -f init.sql
make install