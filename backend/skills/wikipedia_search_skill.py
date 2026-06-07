import urllib.request
import urllib.parse
import json

TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "search_wikipedia",
        "description": "Pesquisa nativamente na Wikipedia por um termo, entidade ou evento e devolve o resumo do artigo.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "O termo a pesquisar (ex: 'Revolução Francesa', 'Steve Jobs', 'Buraco Negro')"
                },
                "language": {
                    "type": "string",
                    "description": "O código da língua (ex: 'pt' para Português, 'en' para Inglês). Padrão: 'pt'."
                }
            },
            "required": ["query"]
        }
    }
}

def execute(args):
    query = args.get("query", "")
    lang = args.get("language", "pt")
    
    try:
        search_url = f"https://{lang}.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&utf8=&format=json"
        req = urllib.request.Request(search_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            search_data = json.loads(response.read().decode('utf-8'))
            
        if not search_data.get('query', {}).get('search'):
            return f"Nenhum resultado encontrado na Wikipedia ({lang}) para '{query}'."
            
        title = search_data['query']['search'][0]['title']
        
        extract_url = f"https://{lang}.wikipedia.org/w/api.php?action=query&prop=extracts&exintro&explaintext&titles={urllib.parse.quote(title)}&format=json"
        req2 = urllib.request.Request(extract_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req2) as response2:
            extract_data = json.loads(response2.read().decode('utf-8'))
            
        pages = extract_data['query']['pages']
        page_id = list(pages.keys())[0]
        summary = pages[page_id].get('extract', 'Resumo não disponível.')
        
        return f"Resumo da Wikipedia sobre '{title}':\n\n{summary}"
    except Exception as e:
        return f"Erro a pesquisar na Wikipedia: {e}"
