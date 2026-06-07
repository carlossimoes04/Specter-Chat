
TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "competitive_ads_extractor",
        "description": "Baseado no awesome-llm-skills: Extracts and analyzes competitors' ads from ad libraries (Facebook, LinkedIn, etc.) to understand what messaging, problems, and creative approaches are working. Helps inspire and improve your own ad campaigns.",
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
    return f"(Instrução ao LLM: Executa a skill competitive-ads-extractor considerando as suas diretrizes, com base na seguinte entrada: {{input_data}})"
