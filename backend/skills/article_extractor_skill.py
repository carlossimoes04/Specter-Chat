
TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "article_extractor",
        "description": "Baseado no awesome-llm-skills: Lê e extrai apenas o conteúdo limpo e textual de páginas web, ignorando anúncios e navegação.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL do artigo web a extrair"
                }
            } if True else {},
            "required": ["url"]
        }
    }
}

import urllib.request
import re

def execute(args):
    url = args.get('url')
    if not url: return "URL vazia"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as res:
            html = res.read().decode('utf-8', errors='ignore')
            paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', html, re.DOTALL | re.IGNORECASE)
            text = "\n\n".join([re.sub(r'<[^>]+>', '', p).strip() for p in paragraphs if p.strip()])
            return f"Texto extraído:\n{text[:3000]}..." # Limite
    except Exception as e:
        return f"Erro a extrair artigo: {e}"