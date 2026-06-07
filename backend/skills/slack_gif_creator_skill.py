
TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "slack_gif_creator",
        "description": "Baseado no awesome-llm-skills: Toolkit for creating animated GIFs optimized for Slack, with validators for size constraints and composable animation primitives. This skill applies when users request animated GIFs or emoji animations for Slack from descriptions like 'make me a GIF for Slack of X doing Y'.",
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
    return f"(Instrução ao LLM: Executa a skill slack-gif-creator considerando as suas diretrizes, com base na seguinte entrada: {{input_data}})"
