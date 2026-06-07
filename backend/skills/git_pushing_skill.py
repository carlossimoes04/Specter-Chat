
TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "git_pushing",
        "description": "Baseado no awesome-llm-skills: Automação completa de git add, commit com mensagem estruturada, e push para a cloud.",
        "parameters": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "A mensagem detalhada do commit a submeter"
                }
            } if True else {},
            "required": ["message"]
        }
    }
}

import subprocess
import os

def execute(args):
    path = '.'
    msg = args.get('message', 'Update')
    try:
        subprocess.run(["git", "add", "."], cwd=path, check=True)
        subprocess.run(["git", "commit", "-m", msg], cwd=path, check=True)
        res = subprocess.run(["git", "push"], cwd=path, capture_output=True, text=True)
        return f"Git Push concluído:\n{res.stdout}\n{res.stderr}"
    except Exception as e:
        return f"Erro no Git: {e}"