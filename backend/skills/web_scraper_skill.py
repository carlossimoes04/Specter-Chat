import urllib.request
import urllib.error
import re

TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "scrape_web_page",
        "description": "Extrai o texto bruto e limpo de qualquer página Web usando um URL. Útil para ler documentação, artigos ou notícias.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "O link completo (URL) da página a ler (ex: 'https://pt.wikipedia.org/wiki/Inteligência_artificial')"
                }
            },
            "required": ["url"]
        }
    }
}

def clean_html(html_text):
    # Remove scripts e styles
    text = re.sub(r'<script.*?>.*?</script>', '', html_text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<style.*?>.*?</style>', '', text, flags=re.IGNORECASE | re.DOTALL)
    # Remove as tags HTML e deixa apenas o texto
    text = re.sub(r'<[^>]+>', ' ', text)
    # Limpa espaços em branco excessivos
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def execute(args):
    url = args.get("url", "")
    if not url.startswith("http"):
        url = "https://" + url
        
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=10) as response:
            html_data = response.read().decode('utf-8')
            
        clean_text = clean_html(html_data)
        
        # Limitar o texto devolvido para não rebentar o limite de tokens do LLM
        max_length = 3000
        if len(clean_text) > max_length:
            clean_text = clean_text[:max_length] + "... [CONTEÚDO TRUNCADO]"
            
        return f"Conteúdo extraído de {url}:\n\n{clean_text}"
    except urllib.error.URLError as e:
        return f"Erro de ligação: Não foi possível aceder ao URL. {e.reason}"
    except Exception as e:
        return f"Erro ao extrair página Web: {e}"
