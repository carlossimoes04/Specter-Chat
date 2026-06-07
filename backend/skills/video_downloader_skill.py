
TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "video_downloader",
        "description": "Baseado no awesome-llm-skills: Downloads videos from YouTube and other platforms for offline viewing, editing, or archival. Handles various formats and quality options.",
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
    return f"(Instrução ao LLM: Executa a skill video-downloader considerando as suas diretrizes, com base na seguinte entrada: {{input_data}})"
