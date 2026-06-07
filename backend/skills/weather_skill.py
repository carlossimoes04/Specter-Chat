import urllib.request
import urllib.parse

TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Obtém a previsão do tempo e a temperatura atual para uma cidade específica.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "O nome da cidade para a qual se quer obter a meteorologia (ex: 'Lisbon', 'Porto', 'London')"
                }
            },
            "required": ["city"]
        }
    }
}

def execute(args):
    city = args.get("city", "Lisbon")
    try:
        # Usa um serviço público simples de meteorologia sem necessidade de API key
        url = f"https://wttr.in/{urllib.parse.quote(city)}?format=%C,+%t"
        req = urllib.request.Request(url, headers={'User-Agent': 'curl/7.68.0'})
        with urllib.request.urlopen(req) as response:
            data = response.read().decode('utf-8')
        return f"A meteorologia atual em {city} é: {data}"
    except Exception as e:
        return f"Erro ao contactar serviço de meteorologia: {e}"
