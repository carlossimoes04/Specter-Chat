
TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "content_research_writer",
        "description": "Baseado no awesome-llm-skills: Assists in writing high-quality content by conducting research, adding citations, improving hooks, iterating on outlines, and providing real-time feedback on each section. Transforms your writing process from solo effort to collaborative partnership.",
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
    return f"(Instrução ao LLM: Executa a skill content-research-writer considerando as suas diretrizes, com base na seguinte entrada: {{input_data}})"
