
TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "file_organizer",
        "description": "Baseado no awesome-llm-skills: Lê ficheiros numa pasta para ajudar a organizar, categorizar e renomear sistematicamente.",
        "parameters": {
            "type": "object",
            "properties": {
                "folder_path": {
                    "type": "string",
                    "description": "Caminho da pasta que precisa de organização"
                }
            } if True else {},
            "required": ["folder_path"]
        }
    }
}

import os

def execute(args):
    path = args.get('folder_path', '.')
    if not os.path.exists(path): return "Erro: Pasta não existe."
    try:
        files = os.listdir(path)
        return f"Ficheiros encontrados na pasta '{path}':\n" + "\n".join(files) + "\n(Sugere categorias e pastas baseadas nas extensões)"
    except Exception as e:
        return f"Erro: {e}"