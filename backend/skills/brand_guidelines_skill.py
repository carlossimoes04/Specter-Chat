
TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "brand_guidelines",
        "description": "Baseado no awesome-llm-skills: Valida e impõe diretrizes de marca num texto, melhorando a consistência corporativa.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "O texto corporativo que requer análise de tom e consistência"
                }
            } if True else {},
            "required": ["text"]
        }
    }
}

def execute(args):
    text = args.get('text', '')
    if not text: return "Sem texto submetido."
    return f"(Instrução ao LLM: Recebeste o texto com {len(text.split())} palavras. A tua tarefa agora é reescrevê-lo utilizando a Brand Guideline oficial: Voz Positiva, Ativa, Inclusiva e Profissional. Apresenta o Antes e o Depois.)"