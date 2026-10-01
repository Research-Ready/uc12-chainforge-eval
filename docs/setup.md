# UC12 ChainForge Eval — Setup Guide

## Prerequisites

Python 3.10+ and pip. Local Ollama running with the models listed below.

---

## 1. Install ChainForge

```bash
pip install chainforge
```

---

## 2. Start the Server

Use port 8765 to avoid conflicts with the local stack (see Port Reference below).

```bash
chainforge serve --port 8765
```

Open `http://localhost:8765` in your browser.

---

## 3. Connect Local Ollama Models

In ChainForge, add a new provider:

- **Provider type:** OpenAI (ChainForge uses OpenAI-compatible format)
- **Base URL:** `http://localhost:11434/v1`
- **API key:** `ollama` (literal string — Ollama ignores the value but requires a non-empty key)
- **Model names to use:**
  - `hermes3:latest`
  - `qwen3:14b`
  - `gemma3:27b`
  - `phi4:latest`
  - `deepseek-r1:14b`
  - `llama3.1:8b`

---

## 4. Connect External Models

Set API keys in `.env` (copy from `.env.example`):

```bash
cp .env.example .env
# edit .env and fill in keys
```

In ChainForge:

- **Anthropic:** add provider → Anthropic → paste `ANTHROPIC_API_KEY`
- **OpenAI:** add provider → OpenAI → paste `OPENAI_API_KEY`
- **Google:** add provider → Google → paste `GOOGLE_API_KEY`

---

## 5. Connect a Remote Ollama Instance (GPU Rig)

If Ollama is running on a separate machine on the local network:

- **Base URL:** `http://<GPU_RIG_IP>:11434/v1`
- Replace `<GPU_RIG_IP>` with the remote host's LAN IP (e.g. `192.168.1.42`)
- Ensure the remote machine's firewall allows inbound TCP on port 11434
- All other settings are the same as local Ollama above

---

## 6. Import Flow Files

1. Open ChainForge at `http://localhost:8765`
2. Click **File → Import** (or drag-and-drop)
3. Select a `.cforge` file from `chainforge/flows/`
4. The flow opens with all nodes pre-wired

---

## 7. Export Results

After a run completes:

- **CSV:** click the Inspect node → Export → CSV → save to `output/runs/`
- **JSON:** same menu, choose JSON format
- Both formats are gitignored; commit only summaries to `output/`

---

## Port Reference — Conflicts to Avoid

| Port | Service |
|------|---------|
| 3000 | OpenWebUI |
| 5678 | n8n |
| 8000 | LangGraph |
| **8765** | **ChainForge (this project)** |
| 11434 | Ollama |

---

## Troubleshooting

**ChainForge won't start:** check `lsof -i :8765` for a port conflict.

**Ollama models not appearing:** verify `ollama list` shows the model and the base URL ends with `/v1`.

**Slow responses on large models:** `gemma3:27b` and `deepseek-r1:14b` need significant VRAM — check `ollama ps` to confirm the model is loaded, not swapping.
