import subprocess
import os

TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "generate_changelog_from_git",
        "description": "Skill baseada no 'Changelog Generator' do awesome-llm-skills: Lê o histórico de commits do git para extrair as alterações e ajudar a gerar um Changelog detalhado.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "O caminho para a pasta do repositório Git local (usa '.' para a diretoria atual)"
                },
                "max_commits": {
                    "type": "integer",
                    "description": "Número máximo de commits a ler (padrão: 30)"
                }
            },
            "required": ["path"]
        }
    }
}

def execute(args):
    repo_path = args.get("path", ".")
    max_commits = args.get("max_commits", 30)
    
    try:
        if not os.path.exists(repo_path):
            return f"Erro: O diretório '{repo_path}' não existe."
            
        result = subprocess.run(
            ["git", "log", f"-n{max_commits}", "--pretty=format:%h | %s | %cr | %an"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return f"Erro ao aceder ao Git (certifica-te que é um repositório git válido): {result.stderr}"
            
        commits = result.stdout.strip()
        if not commits:
            return "Nenhum commit encontrado."
            
        return (f"Histórico de Commits (últimos {max_commits} no formato: Hash | Mensagem | Data | Autor):\n\n{commits}\n\n"
                "-> Instrução para o Bot: Usa estes commits para redigir um Changelog profissional, agrupando por Novidades (Features), Correções (Fixes) e Tarefas Técnicas (Chores).")
    except Exception as e:
        return f"Erro interno: {e}"
