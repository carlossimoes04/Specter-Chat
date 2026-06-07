import urllib.request
import json

TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_crypto_price",
        "description": "Obtém o preço atual de uma criptomoeda em USD (Dólares) e EUR (Euros) em tempo real.",
        "parameters": {
            "type": "object",
            "properties": {
                "coin_id": {
                    "type": "string",
                    "description": "O ID da criptomoeda (ex: 'bitcoin', 'ethereum', 'dogecoin')"
                }
            },
            "required": ["coin_id"]
        }
    }
}

def execute(args):
    coin_id = args.get("coin_id", "bitcoin").lower()
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd,eur"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            
        if coin_id in data:
            prices = data[coin_id]
            return f"O preço atual da moeda '{coin_id}' é:\n- USD: ${prices.get('usd')}\n- EUR: €{prices.get('eur')}"
        else:
            return f"Erro: Criptomoeda '{coin_id}' não encontrada na base de dados (verifica se o ID está correto)."
    except Exception as e:
        return f"Erro ao obter preço da criptomoeda: {e}"
