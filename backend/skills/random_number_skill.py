import random

TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "generate_random_number",
        "description": "Gera um número aleatório inteiro entre um valor mínimo e um valor máximo.",
        "parameters": {
            "type": "object",
            "properties": {
                "min": {
                    "type": "integer",
                    "description": "O valor mínimo (inclusivo)"
                },
                "max": {
                    "type": "integer",
                    "description": "O valor máximo (inclusivo)"
                }
            },
            "required": ["min", "max"]
        }
    }
}

def execute(args):
    try:
        min_val = int(args.get("min", 1))
        max_val = int(args.get("max", 100))
        if min_val > max_val:
            return "Erro: O valor mínimo não pode ser maior que o máximo."
            
        res = random.randint(min_val, max_val)
        return f"Número gerado: {res}"
    except Exception as e:
        return f"Erro ao gerar número: {e}"
