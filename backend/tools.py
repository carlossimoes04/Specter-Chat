from duckduckgo_search import DDGS
import os

def search_web(query: str) -> str:
    """Pesquisa na web."""
    try:
        results = DDGS().text(query, max_results=3)
        return str(results)
    except Exception as e:
        return f"Erro na pesquisa web: {str(e)}"

def list_directory(path: str) -> str:
    """Lista diretórios."""
    try:
        real_path = os.path.expanduser(path)
        if not os.path.exists(real_path):
            return f"Diretório não encontrado: {path}"
        contents = os.listdir(real_path)
        return str(contents)
    except Exception as e:
        return f"Erro ao listar diretório: {str(e)}"

def read_file(path: str) -> str:
    """Lê um ficheiro."""
    try:
        real_path = os.path.expanduser(path)
        if not os.path.exists(real_path):
            return f"Ficheiro não encontrado: {path}"
        with open(real_path, 'r', encoding='utf-8') as f:
            return f.read()[:2000] # Limitado a 2000 chars para não rebentar o contexto
    except Exception as e:
        return f"Erro ao ler ficheiro: {str(e)}"

def write_file(path: str, content: str) -> str:
    """Escreve conteúdo num ficheiro."""
    try:
        real_path = os.path.expanduser(path)
        with open(real_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Ficheiro guardado com sucesso em: {real_path}"
    except Exception as e:
        return f"Erro ao escrever ficheiro: {str(e)}"

import subprocess

def run_command(command: str) -> str:
    """Executa um comando na shell do sistema operativo."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        output = result.stdout
        if result.stderr:
            output += f"\n[ERROS/AVISOS]:\n{result.stderr}"
        if not output.strip():
            output = "[O comando foi executado com sucesso e não devolveu texto.]"
        return output[:4000] # Limite para não rebentar contexto
    except subprocess.TimeoutExpired:
        return "[Erro] O comando demorou mais de 30 segundos a responder e foi cancelado."
    except Exception as e:
        return f"[Erro fatal no comando]: {str(e)}"
