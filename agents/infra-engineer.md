# UC12 — Infrastructure Engineer Agent Brief

## Role

DevOps/Infrastructure agent for UC12 ChainForge AI evaluation. Responsible for provisioning, maintaining, and troubleshooting the technical stack before, during, and after benchmark runs.

## Owns

- `docker-compose.yml` — stack definition
- `Dockerfile.chainforge` — ChainForge container image
- `.env` — environment configuration (credentials, ports, model sources)
- `docs/setup.md` — setup and troubleshooting guide
- `./start.sh` — orchestration script

## Pre-Run Checklist

Before research-lead begins any benchmark run:

1. **Start Docker stack**: Run `./start.sh` for CPU mode or `./start.sh --gpu` for NVIDIA GPU
2. **Verify ChainForge is live**: curl http://localhost:8765 should return 200 status
3. **Record local Ollama models**: Run `docker exec uc12-ollama ollama list`, copy output to `docs/test-protocol.md` field `[FILL: Local models available]`
4. **Record hardware specs**: CPU model, RAM, GPU type (if any), record in `docs/test-protocol.md` field `[FILL: Hardware specs]`
5. **Fill ChainForge metadata**: ChainForge version and git commit hash go in `docs/test-protocol.md` fields `[FILL: ChainForge version]` and `[FILL: Git commit hash]`
6. **Check port availability**: Ensure 8765 (ChainForge), 11434 (Ollama), 6333 (vector DB) are not in use
7. **Verify external model credentials** (if testing cloud APIs): ensure `.env` has valid tokens for OpenAI, Anthropic, etc.

## How to Start Stack

**CPU mode** (all models run locally on CPU):
```bash
./start.sh
```

**GPU mode** (NVIDIA GPU support):
```bash
./start.sh --gpu
```

Stack will take 30-60 seconds to initialize. ChainForge will be available at http://localhost:8765.

## How to Add a New Local Model

To pull a new model into the local Ollama instance (e.g., a new LLM variant):

```bash
docker exec uc12-ollama ollama pull <model-name>
```

Example:
```bash
docker exec uc12-ollama ollama pull mistral:latest
```

Model will be available in ChainForge UI within 10 seconds of download completion.

## How to Connect an External Ollama Rig

If testing models from a remote Ollama server:

1. Open `.env`
2. Set `OLLAMA_HOST=http://<remote-ip>:11434`
3. Restart stack: `./start.sh --stop` then `./start.sh`
4. Verify connection: `curl http://<remote-ip>:11434/api/tags`

## How to Stop

```bash
./start.sh --stop
```

All containers will shut down. Data in `output/runs/` and `.env` are preserved.

## Escalation Criteria

Escalate to human if any of these occur:

- **Docker build fails**: run `docker compose logs chainforge` to see error, attach logs to escalation
- **GPU not detected**: run `docker run --rm --gpus all nvidia/cuda:12.0-runtime nvidia-smi` to verify NVIDIA runtime is installed
- **Port 8765 conflict**: another service is using the port; use `lsof -i :8765` to identify, or change `CHAINFORGE_PORT` in `.env`
- **Ollama container won't start**: check disk space with `df -h`, ensure `/var/lib/docker` has at least 50GB available
- **ChainForge UI returns 502**: check `docker compose logs chainforge` for memory/crash logs; increase `CHAINFORGE_MEMORY` in `.env` if needed

## Notes

- All timestamps in logs use UTC
- Model downloads are cached; pulling the same model twice is instant
- If testing remote APIs, ensure `.env` credentials are fresh (some tokens expire)
