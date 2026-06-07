
TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "notion_knowledge_capture",
        "description": "Baseado no awesome-llm-skills: Transforms conversations and discussions into structured documentation pages in Notion. Captures insights, decisions, and knowledge from chat context, formats appropriately, and saves to wikis or databases with proper organization and linking for easy discovery.",
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
    return f"(Instrução ao LLM: Executa a skill notion-knowledge-capture considerando as suas diretrizes, com base na seguinte entrada: {{input_data}})"
