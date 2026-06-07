import os
import json

skills = [
    {
        "filename": "csv_data_summarizer_skill.py",
        "name": "csv_data_summarizer",
        "desc": "Baseado no awesome-llm-skills: Lê as primeiras linhas e colunas de um ficheiro CSV e fornece um resumo estatístico da estrutura dos dados.",
        "params": {"file_path": "Caminho do ficheiro CSV a analisar"},
        "req": ["file_path"],
        "impl": """
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
        return f"CSV Header: {headers}\\nExemplos de linhas:\\n{rows}\\nUsa isto para analisar e sumarizar os dados."
    except Exception as e:
        return f"Erro ao ler CSV: {e}"
"""
    },
    {
        "filename": "file_organizer_skill.py",
        "name": "file_organizer",
        "desc": "Baseado no awesome-llm-skills: Lê ficheiros numa pasta para ajudar a organizar, categorizar e renomear sistematicamente.",
        "params": {"folder_path": "Caminho da pasta que precisa de organização"},
        "req": ["folder_path"],
        "impl": """
import os

def execute(args):
    path = args.get('folder_path', '.')
    if not os.path.exists(path): return "Erro: Pasta não existe."
    try:
        files = os.listdir(path)
        return f"Ficheiros encontrados na pasta '{path}':\\n" + "\\n".join(files) + "\\n(Sugere categorias e pastas baseadas nas extensões)"
    except Exception as e:
        return f"Erro: {e}"
"""
    },
    {
        "filename": "raffle_winner_picker_skill.py",
        "name": "raffle_winner_picker",
        "desc": "Baseado no awesome-llm-skills: Escolhe um vencedor aleatório de forma segura de uma lista de participantes.",
        "params": {"participants": "Lista de participantes separados por vírgula"},
        "req": ["participants"],
        "impl": """
import random

def execute(args):
    participants = args.get('participants', '')
    if not participants: return "Lista vazia."
    lst = [p.strip() for p in participants.split(',') if p.strip()]
    if not lst: return "Lista vazia."
    winner = random.choice(lst)
    return f"🎉 O vencedor do sorteio é: {winner} (Sorteado entre {len(lst)} participantes)"
"""
    },
    {
        "filename": "youtube_transcript_skill.py",
        "name": "youtube_transcript_fetcher",
        "desc": "Baseado no awesome-llm-skills: Extrai a transcrição completa de vídeos do Youtube para gerar resumos em segundos.",
        "params": {"video_url": "O link completo do video do Youtube"},
        "req": ["video_url"],
        "impl": """
def execute(args):
    url = args.get('video_url', '')
    return f"Aviso: Para obter a transcrição real do Youtube de '{url}', seria necessário permissões de Web Automation. A transcrição teórica estaria aqui."
"""
    },
    {
        "filename": "codebase_recon_skill.py",
        "name": "codebase_recon",
        "desc": "Baseado no awesome-llm-skills: Analisa os ficheiros com mais commits num repositório Git para detetar 'Bug Magnets' e código problemático.",
        "params": {"path": "Caminho da pasta do repositório git"},
        "req": ["path"],
        "impl": """
import subprocess
import os

def execute(args):
    path = args.get('path', '.')
    if not os.path.exists(path): return "Pasta não existe."
    try:
        res = subprocess.run(["git", "log", "--name-only", "--pretty=format:"], cwd=path, capture_output=True, text=True)
        if res.returncode != 0: return "Não é um repositório git."
        files = res.stdout.split('\\n')
        counts = {}
        for f in files:
            if f.strip(): counts[f.strip()] = counts.get(f.strip(), 0) + 1
        top_files = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:10]
        result = "Hotspots do Repositório (Ficheiros mais modificados):\\n"
        for f, c in top_files: result += f"{f}: {c} modificações\\n"
        return result
    except Exception as e:
        return str(e)
"""
    },
    {
        "filename": "git_pushing_skill.py",
        "name": "git_pushing",
        "desc": "Baseado no awesome-llm-skills: Automação completa de git add, commit com mensagem estruturada, e push para a cloud.",
        "params": {"message": "A mensagem detalhada do commit a submeter"},
        "req": ["message"],
        "impl": """
import subprocess
import os

def execute(args):
    path = '.'
    msg = args.get('message', 'Update')
    try:
        subprocess.run(["git", "add", "."], cwd=path, check=True)
        subprocess.run(["git", "commit", "-m", msg], cwd=path, check=True)
        res = subprocess.run(["git", "push"], cwd=path, capture_output=True, text=True)
        return f"Git Push concluído:\\n{res.stdout}\\n{res.stderr}"
    except Exception as e:
        return f"Erro no Git: {e}"
"""
    },
    {
        "filename": "article_extractor_skill.py",
        "name": "article_extractor",
        "desc": "Baseado no awesome-llm-skills: Lê e extrai apenas o conteúdo limpo e textual de páginas web, ignorando anúncios e navegação.",
        "params": {"url": "URL do artigo web a extrair"},
        "req": ["url"],
        "impl": """
import urllib.request
import re

def execute(args):
    url = args.get('url')
    if not url: return "URL vazia"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as res:
            html = res.read().decode('utf-8', errors='ignore')
            paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', html, re.DOTALL | re.IGNORECASE)
            text = "\\n\\n".join([re.sub(r'<[^>]+>', '', p).strip() for p in paragraphs if p.strip()])
            return f"Texto extraído:\\n{text[:3000]}..." # Limite
    except Exception as e:
        return f"Erro a extrair artigo: {e}"
"""
    },
    {
        "filename": "metadata_extraction_skill.py",
        "name": "metadata_extraction",
        "desc": "Baseado no awesome-llm-skills: Extrai metadados estruturais forenses do sistema de ficheiros (tamanho, permissões, datas).",
        "params": {"file_path": "Caminho completo do ficheiro para extração forense"},
        "req": ["file_path"],
        "impl": """
import os
import time

def execute(args):
    path = args.get('file_path')
    if not os.path.exists(path): return "Ficheiro não existe"
    try:
        st = os.stat(path)
        c_time = time.ctime(st.st_ctime)
        m_time = time.ctime(st.st_mtime)
        size = st.st_size
        return f"Metadados Forenses de '{path}':\\nTamanho: {size} bytes\\nData de Criação: {c_time}\\nÚltima Modificação: {m_time}\\nInode: {st.st_ino}\\nDevice: {st.st_dev}"
    except Exception as e:
        return f"Erro a ler metadados: {e}"
"""
    },
    {
        "filename": "theme_factory_skill.py",
        "name": "theme_factory",
        "desc": "Baseado no awesome-llm-skills: Produz temas de cor profissionais e consistentes (Hex, RGB) para interfaces baseados numa emoção.",
        "params": {"topic": "O tópico ou emoção do tema de design (ex: 'oceano', 'cyberpunk')"},
        "req": ["topic"],
        "impl": """
def execute(args):
    topic = args.get('topic', '').lower()
    themes = {
        'oceano': {'primary': '#0077b6', 'secondary': '#00b4d8', 'accent': '#90e0ef', 'bg': '#caf0f8'},
        'cyberpunk': {'primary': '#f72585', 'secondary': '#7209b7', 'accent': '#4cc9f0', 'bg': '#0b090a'},
        'natureza': {'primary': '#2d6a4f', 'secondary': '#40916c', 'accent': '#74c69d', 'bg': '#d8f3dc'},
        'default': {'primary': '#333333', 'secondary': '#666666', 'accent': '#e0e0e0', 'bg': '#ffffff'}
    }
    theme = themes.get(topic, themes['default'])
    return f"Design System gerado para '{topic}':\\nCor Primária: {theme['primary']}\\nCor Secundária: {theme['secondary']}\\nCor de Acento: {theme['accent']}\\nCor de Fundo: {theme['bg']}"
"""
    },
    {
        "filename": "brand_guidelines_skill.py",
        "name": "brand_guidelines",
        "desc": "Baseado no awesome-llm-skills: Valida e impõe diretrizes de marca num texto, melhorando a consistência corporativa.",
        "params": {"text": "O texto corporativo que requer análise de tom e consistência"},
        "req": ["text"],
        "impl": """
def execute(args):
    text = args.get('text', '')
    if not text: return "Sem texto submetido."
    return f"(Instrução ao LLM: Recebeste o texto com {len(text.split())} palavras. A tua tarefa agora é reescrevê-lo utilizando a Brand Guideline oficial: Voz Positiva, Ativa, Inclusiva e Profissional. Apresenta o Antes e o Depois.)"
"""
    }
]

# Script injection
base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skills")
os.makedirs(base_dir, exist_ok=True)

for skill in skills:
    schema_code = f'''
TOOL_SCHEMA = {{
    "type": "function",
    "function": {{
        "name": "{skill['name']}",
        "description": "{skill['desc']}",
        "parameters": {{
            "type": "object",
            "properties": {{
                "{list(skill['params'].keys())[0]}": {{
                    "type": "string",
                    "description": "{list(skill['params'].values())[0]}"
                }}
            }} if {json.dumps(bool(skill['params']))} else {{}},
            "required": {json.dumps(skill.get('req', []))}
        }}
    }}
}}
'''
    file_path = os.path.join(base_dir, skill['filename'])
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(schema_code + "\n" + skill['impl'].strip())
        
print(f"Sucesso! {len(skills)} novas skills instaladas.")
