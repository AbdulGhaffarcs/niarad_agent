---
title: NIARAD Agent Backend
emoji: N
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
app_port: 7860
---

# NIARAD Agent Backend

FastAPI backend for NIARAD Agent, packaged as a Hugging Face Docker Space.

## Required Space secrets

Set these in the Space settings:

- `GROQ_API_KEY`: your Groq API key.
- `FRONTEND_ORIGINS`: comma-separated frontend URLs, for example `https://your-vercel-app.vercel.app`.

## Runtime storage

The Docker image defaults `NIARAD_DATA_DIR` to `/data`, so SQLite study data, FAISS indexes, and generated files can survive restarts when persistent storage is enabled for the Space.

## Health check

After the Space builds, open:

```text
https://<username>-<space-name>.hf.space/
```

Expected response:

```json
{"status":"NIARAD Agent API online","version":"3.1.0"}
```
