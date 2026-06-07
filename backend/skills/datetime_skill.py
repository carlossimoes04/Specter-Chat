from datetime import datetime

TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_current_datetime",
        "description": "Retorna a data e a hora atual do sistema local.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}

def execute(args):
    now = datetime.now()
    return f"A data e hora atual do sistema é: {now.strftime('%Y-%m-%d %H:%M:%S')}"
