
TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "notion_research_documentation",
        "description": "Baseado no awesome-llm-skills: Searches across your Notion workspace, synthesizes findings from multiple pages, and creates comprehensive research documentation saved as new Notion pages. Turns scattered information into structured reports with proper citations and actionable insights.",
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
    return f"(Instrução ao LLM: Executa a skill notion-research-documentation considerando as suas diretrizes, com base na seguinte entrada: {{input_data}})"
