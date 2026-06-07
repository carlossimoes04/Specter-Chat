import urllib.request
import json

TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_hacker_news",
        "description": "Obtém as notícias e artigos mais relevantes do momento na primeira página do Hacker News (Tecnologia, Ciência e Programação).",
        "parameters": {
            "type": "object",
            "properties": {
                "count": {
                    "type": "integer",
                    "description": "Número de notícias a obter (sugerido: 5). O máximo permitido é 15."
                }
            },
            "required": []
        }
    }
}

def execute(args):
    try:
        count = int(args.get("count", 5))
        if count > 15: count = 15
        
        url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            story_ids = json.loads(response.read().decode('utf-8'))
            
        top_ids = story_ids[:count]
        news_list = []
        
        for i, sid in enumerate(top_ids):
            story_url = f"https://hacker-news.firebaseio.com/v0/item/{sid}.json"
            sreq = urllib.request.Request(story_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(sreq) as sresponse:
                story = json.loads(sresponse.read().decode('utf-8'))
                title = story.get('title', 'Sem título')
                link = story.get('url', f"https://news.ycombinator.com/item?id={sid}")
                score = story.get('score', 0)
                news_list.append(f"{i+1}. {title} ({score} upvotes)\n   Link: {link}")
                
        return "As notícias do momento no Hacker News:\n\n" + "\n\n".join(news_list)
    except Exception as e:
        return f"Erro ao obter Hacker News: {e}"
