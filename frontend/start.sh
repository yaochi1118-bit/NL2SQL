#!/usr/bin/env bash
# Start the DDL-to-SQL web application
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "Building frontend..."
cd "$SCRIPT_DIR"
npm run build

echo "Starting backend server..."
cd "$PROJECT_DIR"
uv run uvicorn my_tool.api.server:app --host 127.0.0.1 --port 8000
