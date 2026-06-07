
TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "csv_data_summarizer",
        "description": "Baseado no awesome-llm-skills: Lê as primeiras linhas e colunas de um ficheiro CSV e fornece um resumo estatístico da estrutura dos dados.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Caminho do ficheiro CSV a analisar"
                }
            } if True else {},
            "required": ["file_path"]
        }
    }
}

import csv
import os

def execute(args):
    path = args.get('file_path')
    if not os.path.exists(path): return f"Erro: {path} não existe."
    try:
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader, None)
            if not headers: return "Ficheiro CSV vazio."
            rows = []
            for i, row in enumerate(reader):
                if i < 5: rows.append(row)
                else: break
        return f"CSV Header: {headers}\nExemplos de linhas:\n{rows}\nUsa isto para analisar e sumarizar os dados."
    except Exception as e:
        return f"Erro ao ler CSV: {e}"