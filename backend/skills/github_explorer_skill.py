import urllib.request
import urllib.error
import json

TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "read_github_repo",
        "description": "Explora a estrutura de ficheiros principal de um repositório público do GitHub e obtém a descrição do projeto.",
        "parameters": {
            "type": "object",
            "properties": {
                "owner": {
                    "type": "string",
                    "description": "Nome do dono do repositório (ex: 'facebook')"
                },
                "repo": {
                    "type": "string",
                    "description": "Nome do repositório (ex: 'react')"
                }
            },
            "required": ["owner", "repo"]
        }
    }
}

def execute(args):
    owner = args.get("owner", "")
    repo = args.get("repo", "")
    if not owner or not repo:
        return "Erro: owner e repo são obrigatórios."
        
    try:
        # Busca detalhes do repositório
        repo_url = f"https://api.github.com/repos/{owner}/{repo}"
        req = urllib.request.Request(repo_url, headers={'User-Agent': 'Specter-Bot'})
        with urllib.request.urlopen(req) as response:
            repo_data = json.loads(response.read().decode('utf-8'))
            
        # Busca a árvore principal (pasta raiz)
        contents_url = f"https://api.github.com/repos/{owner}/{repo}/contents"
        req_contents = urllib.request.Request(contents_url, headers={'User-Agent': 'Specter-Bot'})
        with urllib.request.urlopen(req_contents) as response:
            contents_data = json.loads(response.read().decode('utf-8'))
            
        files_list = [f"- {item['name']} ({item['type']})" for item in contents_data[:15]]
        
        return f"Repositório: {repo_data.get('full_name')}\nDescrição: {repo_data.get('description')}\nEstrelas: {repo_data.get('stargazers_count')}\n\nFicheiros principais (Raiz):\n" + "\n".join(files_list)
        
    except urllib.error.HTTPError as e:
        return f"Erro HTTP do GitHub API: {e.code}. O repositório pode ser privado ou não existir."
    except Exception as e:
        return f"Erro ao ler repositório: {e}"
