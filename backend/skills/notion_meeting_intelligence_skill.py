
TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "notion_meeting_intelligence",
        "description": "Baseado no awesome-llm-skills: Prepares meeting materials by gathering context from Notion, enriching with Claude research, and creating both an internal pre-read and external agenda saved to Notion. Helps you arrive prepared with comprehensive background and structured meeting docs.",
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
    return f"(Instrução ao LLM: Executa a skill notion-meeting-intelligence considerando as suas diretrizes, com base na seguinte entrada: {{input_data}})"
