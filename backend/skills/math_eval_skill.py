import math

TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "calculate_math",
        "description": "Avalia uma expressão matemática de forma exata. Os LLMs cometem erros em cálculos complexos, por isso usa esta ferramenta sempre que precisares de somar, multiplicar, ou fazer contas difíceis.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "A expressão matemática em Python a avaliar (ex: '25 * 4 + 10 / 2', 'math.sqrt(144)')"
                }
            },
            "required": ["expression"]
        }
    }
}

def execute(args):
    try:
        expr = args.get("expression", "")
        # Ambiente restrito para segurança mínima
        allowed_names = {
            "math": math, 
            "abs": abs, 
            "round": round, 
            "max": max, 
            "min": min, 
            "pow": pow
        }
        # Avalia a expressão retornando uma string do resultado
        result = eval(expr, {"__builtins__": {}}, allowed_names)
        return str(result)
    except Exception as e:
        return f"Erro ao calcular a expressão '{expr}': {e}"
