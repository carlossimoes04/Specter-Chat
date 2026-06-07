
TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "metadata_extraction",
        "description": "Baseado no awesome-llm-skills: Extrai metadados estruturais forenses do sistema de ficheiros (tamanho, permissões, datas).",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Caminho completo do ficheiro para extração forense"
                }
            } if True else {},
            "required": ["file_path"]
        }
    }
}

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
        return f"Metadados Forenses de '{path}':\nTamanho: {size} bytes\nData de Criação: {c_time}\nÚltima Modificação: {m_time}\nInode: {st.st_ino}\nDevice: {st.st_dev}"
    except Exception as e:
        return f"Erro a ler metadados: {e}"