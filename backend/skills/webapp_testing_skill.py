
TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "webapp_testing",
        "description": "Baseado no awesome-llm-skills: Toolkit for interacting with and testing local web applications using Playwright. Supports verifying frontend functionality, debugging UI behavior, capturing browser screenshots, and viewing browser logs.",
        "parameters": {
            "type": "object",
            "properties": {
                "input_data": {
                    "type": "string",
                    "description": "Os dados de entrada para aplicar a skill"
                }
            },
            "required": ["input_data"]
        }
    }
}

def execute(args):
    input_data = args.get('input_data', '')
    if not input_data: 
        return "Sem dados submetidos."
    return f"(Instrução ao LLM: Executa a skill webapp-testing considerando as suas diretrizes, com base na seguinte entrada: {{input_data}})"
