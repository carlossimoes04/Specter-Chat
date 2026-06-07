
TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "codebase_recon",
        "description": "Baseado no awesome-llm-skills: Analisa os ficheiros com mais commits num repositório Git para detetar 'Bug Magnets' e código problemático.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Caminho da pasta do repositório git"
                }
            } if True else {},
            "required": ["path"]
        }
    }
}

import subprocess
import os

def execute(args):
    path = args.get('path', '.')
    if not os.path.exists(path): return "Pasta não existe."
    try:
        res = subprocess.run(["git", "log", "--name-only", "--pretty=format:"], cwd=path, capture_output=True, text=True)
        if res.returncode != 0: return "Não é um repositório git."
        files = res.stdout.split('\n')
        counts = {}
        for f in files:
            if f.strip(): counts[f.strip()] = counts.get(f.strip(), 0) + 1
        top_files = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:10]
        result = "Hotspots do Repositório (Ficheiros mais modificados):\n"
        for f, c in top_files: result += f"{f}: {c} modificações\n"
        return result
    except Exception as e:
        return str(e)