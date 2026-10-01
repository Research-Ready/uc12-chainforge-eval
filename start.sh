#!/usr/bin/env bash
# UC12 — Quick start script
# Starts ChainForge + Ollama, optionally with GPU support.
#
# Usage:
#   ./start.sh          # CPU mode
#   ./start.sh --gpu    # NVIDIA GPU mode (requires NVIDIA Container Toolkit)
#   ./start.sh --stop   # Stop all services

set -e

if [ "$1" = "--stop" ]; then
  echo "Stopping UC12 stack..."
  docker compose down
  exit 0
fi

if [ ! -f .env ]; then
  echo "No .env found — copying .env.example (external API keys optional)."
  cp .env.example .env
fi

if [ "$1" = "--gpu" ]; then
  echo "Starting UC12 stack (GPU mode)..."
  docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d
else
  echo "Starting UC12 stack (CPU mode)..."
  docker compose up -d
fi

echo ""
echo "ChainForge UI: http://localhost:8765"
echo "Ollama API:    http://localhost:11434"
echo ""
echo "Import a flow from chainforge/flows/ to start benchmarking."
echo "Run './start.sh --stop' to shut down."
