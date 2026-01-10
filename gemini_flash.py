import json, secrets, time, http.client, ssl, os, logging
from flask import Response, request, abort
from searx.plugins import Plugin, PluginInfo
from searx.result_types import EngineResults
from flask_babel import gettext

logger = logging.getLogger(__name__)

class SXNGPlugin(Plugin):
    id = "gemini_flash"

    def __init__(self, plg_cfg):
        super().__init__(plg_cfg)
        self.info = PluginInfo(
            id=self.id,
            name=gettext("Gemini Flash Streaming"),
            description=gettext("Live AI search answers using Google Gemini Flash"),
            preference_section="general", 
        )
        self.active = plg_cfg.active
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model = os.getenv('GEMINI_MODEL', 'gemini-3-flash-preview')
        self.tokens = {}

        if not self.api_key:
            logger.error(f"[{self.id}] API Key missing! Set GEMINI_API_KEY env var.")
        else:
            logger.info(f"[{self.id}] Initialized with model: {self.model}")

    def init(self, app):
        @app.route('/gemini-stream')
        def g_stream():
            t = request.args.get('token')
            q = request.args.get('q', '')
            
            logger.info(f"[{self.id}] Stream requested. Token: {t[:5]}...")

            # Maintenance: Only runs when a stream is requested, not during search.
            current_time = time.time()
            self.tokens = {k: v for k, v in self.tokens.items() if v > current_time}
            
            if t not in self.tokens or not self.api_key:
                logger.warning(f"[{self.id}] Unauthorized stream attempt or missing key.")
                abort(403)
            del self.tokens[t]

            def generate():
                host = "generativelanguage.googleapis.com"
                path = f"/v1beta/models/{self.model}:streamGenerateContent?key={self.api_key}"
                try:
                    logger.info(f"[{self.id}] Connecting to Google API...")
                    context = ssl.create_default_context()
                    conn = http.client.HTTPSConnection(host, context=context)
                    conn.request("POST", path, body=json.dumps({"contents": [{"parts": [{"text": q}]}]}), 
                                 headers={"Content-Type": "application/json"})
                    res = conn.getresponse()
                    
                    logger.info(f"[{self.id}] Google API connected. Streaming...")
                    buffer = ""
                    for chunk in res:
                        buffer += chunk.decode('utf-8')
                        while True:
                            start = buffer.find('{')
                            if start == -1: break
                            brace_count, end = 0, -1
                            for i in range(start, len(buffer)):
                                if buffer[i] == '{': brace_count += 1
                                elif buffer[i] == '}': brace_count -= 1
                                if brace_count == 0:
                                    end = i + 1
                                    break
                            if end == -1: break 
                            try:
                                text = json.loads(buffer[start:end])['candidates'][0]['content']['parts'][0]['text']
                                if text: 
                                    yield text
                                buffer = buffer[end:]
                            except:
                                buffer = buffer[end:]
                    conn.close()
                    logger.info(f"[{self.id}] Stream finished.")
                except Exception as e:
                    logger.error(f"[{self.id}] Stream error: {e}")
                    yield f" [Stream Error: {str(e)}]"

            return Response(generate(), mimetype='text/plain')

    def post_search(self, request, search) -> EngineResults:
        logger.info(f"[{self.id}] post_search hook triggered. Page: {search.search_query.pageno}, Active: {self.active}, Key Present: {bool(self.api_key)}")
        
        results = EngineResults()
        # Page 1 only + check for API key
        if search.search_query.pageno > 1 or not self.active or not self.api_key:
            logger.warning(f"[{self.id}] Skipping injection. Criteria failed.")
            return results

        # ULTRA-LEAN EXECUTION: No loops, no maintenance. Just token creation and return.
        tk = secrets.token_urlsafe(16)
        self.tokens[tk] = time.time() + 90
        
        logger.info(f"[{self.id}] Injecting script for query: {search.search_query.query[:20]}...")

        # Ensure we escape the query properly for JS
        query_json = json.dumps(search.search_query.query)
        
        html = f"""
        <div id="ai-shell" style="display:none; margin-bottom: 2rem; padding: 1.2rem; border-bottom: 1px solid var(--color-result-border);">
            <div id="ai-out" style="line-height: 1.7; white-space: pre-wrap; color: var(--color-result-description); font-size: 0.95rem;"></div>
        </div>
        <script>
            (async () => {{
                const out = document.getElementById('ai-out');
                const shell = document.getElementById('ai-shell');
                try {{
                    const res = await fetch(`/gemini-stream?token={tk}&q=` + encodeURIComponent({query_json}));
                    const reader = res.body.getReader();
                    const decoder = new TextDecoder();
                    while (true) {{
                        const {{done, value}} = await reader.read();
                        if (done) break;
                        const chunk = decoder.decode(value);
                        if (chunk.trim()) {{
                            shell.style.display = 'block';
                            out.innerText += chunk;
                        }}
                    }}
                }} catch (e) {{ console.error("Gemini Failure", e); }}
            }})();
        </script>
        """
        results.add(results.types.Answer(answer=html))
        return results