
TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "algorithmic_art",
        "description": "Baseado no awesome-llm-skills: Creating algorithmic art using p5.js with seeded randomness and interactive parameter exploration. Use this when users request creating art using code, generative art, algorithmic art, flow fields, or particle systems. Create original algorithmic art rather than copying existing artists' work to avoid copyright violations.",
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
    return f"(Instrução ao LLM: Executa a skill algorithmic-art considerando as suas diretrizes, com base na seguinte entrada: {{input_data}})"
