# SearXNG Gemini & OpenRouter Stream

A SearXNG plugin that streams AI responses using search results as grounding context. Supports Google Gemini and OpenAI-compatible providers (OpenRouter, Ollama, etc.).

## Configuration

Set the following environment variables:

### General
- `LLM_PROVIDER`: `gemini` (default) or `openrouter`.
- `GEMINI_MAX_TOKENS`: Defaults to `500`.
- `GEMINI_TEMPERATURE`: Defaults to `0.2`.

### Google Gemini
- `GEMINI_API_KEY`: Your Google AI API key.
- `GEMINI_MODEL`: Defaults to `gemini-1.5-flash`.

### OpenRouter / OpenAI / Ollama
- `OPENROUTER_API_KEY`: Your API key.
- `OPENROUTER_MODEL`: e.g., `meta-llama/llama-3-8b-instruct:free`.
- `OPENROUTER_BASE_URL`: Defaults to `openrouter.ai`. (Change to `localhost:11434` for Ollama).

## Installation

Place `gemini_flash.py` into the `searx/plugins` directory of your instance and enable it in `settings.yml`.