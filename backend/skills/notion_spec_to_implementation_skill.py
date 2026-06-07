
TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "notion_spec_to_implementation",
        "description": "Baseado no awesome-llm-skills: Turns product or tech specs into concrete Notion tasks that Claude code can implement. Breaks down spec pages into detailed implementation plans with clear tasks, acceptance criteria, and progress tracking to guide development from requirements to completion.",
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
    return f"(Instrução ao LLM: Executa a skill notion-spec-to-implementation considerando as suas diretrizes, com base na seguinte entrada: {{input_data}})"
