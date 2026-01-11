# SearXNG Gemini Stream

A SearXNG plugin that streams an AI response using results as grounding context to an Answer box at the top of results.

## Configuration

Set the following environment variables:
- `GEMINI_API_KEY`: Your Google Gemini API key.
- `GEMINI_MODEL`: (Optional) Defaults to `gemini-3-flash-preview`.

### settings.yml
Add this to your SearXNG configuration file to enable the plugin:

```yaml
plugins:
  - name: gemini_flash
    active: true
```

## Installation

Place `gemini_flash.py` into the `searx/plugins` directory of your instance.
