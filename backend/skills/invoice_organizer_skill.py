
TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "invoice_organizer",
        "description": "Baseado no awesome-llm-skills: Automatically organizes invoices and receipts for tax preparation by reading messy files, extracting key information, renaming them consistently, and sorting them into logical folders. Turns hours of manual bookkeeping into minutes of automated organization.",
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
    return f"(Instrução ao LLM: Executa a skill invoice-organizer considerando as suas diretrizes, com base na seguinte entrada: {{input_data}})"
