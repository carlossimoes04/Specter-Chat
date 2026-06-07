from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from llama_cpp import Llama
import json
import tools
import os
import subprocess
import glob
import sys
import importlib
from datetime import datetime
from openai import OpenAI
import chromadb
from chromadb.utils import embedding_functions

# Trigger reload

app = FastAPI(title="Specter Node API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("[Specter] Inicializando motores base...")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CHATS_DIR = os.path.join(DATA_DIR, "chats")
CHROMA_DIR = os.path.join(DATA_DIR, "chroma")

local_engine = {
    "instance": None,
    "loaded_path": None
}

os.makedirs(CHATS_DIR, exist_ok=True)
os.makedirs(CHROMA_DIR, exist_ok=True)

# Inicializar ChromaDB
chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
mem_collection = chroma_client.get_or_create_collection(name="specter_memory", embedding_function=emb_fn)

class ChatRequest(BaseModel):
    messages: list
    mode: str
    model_id: str
    agent_mode: bool = True
    chat_mode: str = 'chat'
    swarm_models: list = []
    search_enabled: bool = False
    terminal_enabled: bool = False
    temperature: float = 0.7
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    channel_id: Optional[str] = None

class SaveChatRequest(BaseModel):
    id: str
    title: str
    messages: list

class MemoryAddRequest(BaseModel):
    text: str
    source: str = "user_input"

tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Searches the web for information using DuckDuckGo. Use this to find recent or external information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query."}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "Lists all files and folders in a given local directory path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "The absolute or relative path to the directory."}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Reads the content of a local file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "The absolute path to the file."}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Writes text or code content to a local file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "The absolute path where the file will be saved."},
                    "content": {"type": "string", "description": "The full text or code content to be written."}
                },
                "required": ["path", "content"]
            }
        }
    }
]

loaded_skills = {}
disabled_skills = set()
loadout_skills = set()
DISABLED_SKILLS_FILE = os.path.join(DATA_DIR, "disabled_skills.json")
LOADOUT_SKILLS_FILE = os.path.join(DATA_DIR, "loadout_skills.json")

if os.path.exists(DISABLED_SKILLS_FILE):
    try:
        with open(DISABLED_SKILLS_FILE, "r", encoding="utf-8") as f:
            disabled_skills = set(json.load(f))
    except Exception as e:
        print(f"[Specter Skills] Erro ao carregar skills desativadas: {e}")
SKILLS_DIR = os.path.join(BASE_DIR, "skills")
os.makedirs(SKILLS_DIR, exist_ok=True)

def load_all_skills():
    global tools_schema, loaded_skills
    # Remover skills customizadas do schema (para não haver duplicados no reload)
    tools_schema = [t for t in tools_schema if t["function"]["name"] not in loaded_skills]
    loaded_skills.clear()
    
    if SKILLS_DIR not in sys.path:
        sys.path.append(SKILLS_DIR)
        
    for file in glob.glob(os.path.join(SKILLS_DIR, "*.py")):
        if file.endswith("__init__.py"): continue
        module_name = os.path.basename(file)[:-3]
        try:
            if module_name in sys.modules:
                mod = importlib.reload(sys.modules[module_name])
            else:
                mod = importlib.import_module(module_name)
                
            if hasattr(mod, "TOOL_SCHEMA") and hasattr(mod, "execute"):
                tools_schema.append(mod.TOOL_SCHEMA)
                loaded_skills[mod.TOOL_SCHEMA["function"]["name"]] = mod.execute
                print(f"[Specter Skills] Módulo '{module_name}' carregado.")
        except Exception as e:
            print(f"[Specter Skills] Erro ao carregar {module_name}: {e}")
            
    global loadout_skills
    if os.path.exists(LOADOUT_SKILLS_FILE):
        try:
            with open(LOADOUT_SKILLS_FILE, "r", encoding="utf-8") as f:
                loadout_skills = set(json.load(f))
        except Exception as e:
            print(f"[Specter Skills] Erro ao carregar loadout: {e}")
    else:
        loadout_skills = set(loaded_skills.keys())
        try:
            with open(LOADOUT_SKILLS_FILE, "w", encoding="utf-8") as f:
                json.dump(list(loadout_skills), f)
        except:
            pass

load_all_skills()

def execute_tool_call(func_name, func_args):
    print(f"[Specter Tool] -> {func_name} | Argumentos: {func_args}")
    if func_name == "search_web":
        return tools.search_web(func_args.get("query", ""))
    elif func_name == "list_directory":
        return tools.list_directory(func_args.get("path", "."))
    elif func_name == "read_file":
        return tools.read_file(func_args.get("path", ""))
    elif func_name == "write_file":
        return tools.write_file(func_args.get("path", ""), func_args.get("content", ""))
    elif func_name == "run_command":
        return tools.run_command(func_args.get("command", ""))
    elif func_name in loaded_skills:
        try:
            return loaded_skills[func_name](func_args)
        except Exception as e:
            return f"Erro na skill {func_name}: {e}"
    else:
        return "Unknown tool"

@app.get("/api/pick-file")
async def pick_file():
    cmd = 'python -c "import tkinter as tk; from tkinter import filedialog; root = tk.Tk(); root.attributes(\'-topmost\', True); root.withdraw(); print(filedialog.askopenfilename(filetypes=[(\'GGUF Models\', \'*.gguf\'), (\'All Files\', \'*.*\')]))"'
    try:
        result = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
        return {"path": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/save")
async def save_chat(req: SaveChatRequest):
    filepath = os.path.join(CHATS_DIR, f"{req.id}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump({"id": req.id, "title": req.title, "messages": req.messages, "updated_at": datetime.now().isoformat()}, f, ensure_ascii=False)
    return {"status": "ok"}

class RenameChatRequest(BaseModel):
    id: str
    title: str

@app.post("/api/chat/rename")
async def rename_chat(req: RenameChatRequest):
    filepath = os.path.join(CHATS_DIR, f"{req.id}.json")
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Chat não encontrado")
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["title"] = req.title
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    return {"status": "ok"}

@app.get("/api/chats")
async def list_chats():
    chats = []
    for filepath in glob.glob(os.path.join(CHATS_DIR, "*.json")):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                chats.append({
                    "id": data.get("id"),
                    "title": data.get("title", "Novo Chat"),
                    "updated_at": data.get("updated_at", "")
                })
        except:
            pass
    chats.sort(key=lambda x: x["updated_at"], reverse=True)
    return chats

@app.get("/api/chat/{chat_id}")
async def load_chat(chat_id: str):
    filepath = os.path.join(CHATS_DIR, f"{chat_id}.json")
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Chat não encontrado")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

@app.delete("/api/chat/{chat_id}")
async def delete_chat(chat_id: str):
    filepath = os.path.join(CHATS_DIR, f"{chat_id}.json")
    if os.path.exists(filepath):
        os.remove(filepath)
    return {"status": "ok"}

@app.post("/api/memory/add")
async def add_memory(req: MemoryAddRequest):
    doc_id = f"mem_{datetime.now().timestamp()}"
    mem_collection.add(
        documents=[req.text],
        metadatas=[{"source": req.source, "date": datetime.now().isoformat()}],
        ids=[doc_id]
    )
    return {"status": "ok", "id": doc_id}

@app.get("/api/memory/search")
async def search_memory(q: str, n: int = 3):
    results = mem_collection.query(
        query_texts=[q],
        n_results=n
    )
    return results

@app.get("/api/memory/all")
async def list_all_memories():
    try:
        data = mem_collection.get()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/memory/{doc_id}")
async def delete_memory(doc_id: str):
    try:
        mem_collection.delete(ids=[doc_id])
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/skills")
async def list_skills():
    load_all_skills() # Forçar reload sempre que abrimos o painel UI
    response = []
    for t in tools_schema:
        name = t["function"]["name"]
        if name in loaded_skills:
            response.append({
                "name": name,
                "description": t["function"]["description"],
                "enabled": name not in disabled_skills,
                "in_loadout": name in loadout_skills
            })
    return response

class SkillStateRequest(BaseModel):
    name: str
    enabled: bool
    in_loadout: bool

@app.post("/api/skills/state")
async def set_skill_state(req: SkillStateRequest):
    if req.in_loadout:
        loadout_skills.add(req.name)
    else:
        loadout_skills.discard(req.name)
        
    if req.enabled:
        disabled_skills.discard(req.name)
    else:
        disabled_skills.add(req.name)
        
    try:
        with open(LOADOUT_SKILLS_FILE, "w", encoding="utf-8") as f:
            json.dump(list(loadout_skills), f)
        with open(DISABLED_SKILLS_FILE, "w", encoding="utf-8") as f:
            json.dump(list(disabled_skills), f)
    except Exception as e:
        print(f"Erro ao salvar estado da skill: {e}")
        
    return {"status": "ok"}

class BulkSkillStateRequest(BaseModel):
    skills: list[dict] # list of {"name": "...", "enabled": bool, "in_loadout": bool}

@app.post("/api/skills/bulk_state")
async def bulk_set_skill_state(req: BulkSkillStateRequest):
    for s in req.skills:
        if s.get("in_loadout"):
            loadout_skills.add(s["name"])
        else:
            loadout_skills.discard(s["name"])
            
        if s.get("enabled"):
            disabled_skills.discard(s["name"])
        else:
            disabled_skills.add(s["name"])
            
    try:
        with open(LOADOUT_SKILLS_FILE, "w", encoding="utf-8") as f:
            json.dump(list(loadout_skills), f)
        with open(DISABLED_SKILLS_FILE, "w", encoding="utf-8") as f:
            json.dump(list(disabled_skills), f)
    except Exception as e:
        print(f"Erro ao salvar estado das skills: {e}")
        
    return {"status": "ok"}

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    
    # Construir histórico limpo para stateless request
    history = []
    
    # Pesquisar contexto na Memória Vetorial (RAG)
    last_user_msg = next((m.get("content", "") for m in reversed(request.messages) if m.get("role") == "user"), "")
    context_str = ""
    if last_user_msg:
        try:
            results = mem_collection.query(query_texts=[last_user_msg], n_results=2)
            if results and results["documents"] and results["documents"][0]:
                context_str = "\n\n[MEMÓRIA DO SISTEMA - Informação recuperada do ChromaDB]:\n" + "\n---\n".join(results["documents"][0])
        except Exception as e:
            print("Aviso: Erro na pesquisa ChromaDB", e)

    if request.search_enabled and last_user_msg:
        try:
            print("[Specter] Executando Web Search forçado...")
            search_res = tools.search_web(last_user_msg)
            context_str += f"\n\n[PESQUISA WEB EM TEMPO REAL (Relevante para a pergunta)]:\n{search_res}"
        except Exception as e:
            print("Aviso: Erro no search forçado", e)

    if not request.messages or request.messages[0].get("role") != "system":
        history.append({
            "role": "system",
            "content": f"You are Specter, an elite, highly capable, and precise AI assistant. Your primary goal is to provide accurate, direct, and actionable answers. You have access to tools for web searching and local file system operations. Always use the most appropriate tool for the task before making assumptions. Think critically and verify information when needed. Answer entirely in US English unless explicitly requested otherwise by the user. Maintain an objective, expert, and concise tone. CRITICAL: You MUST wrap ALL code snippets inside markdown code blocks with the appropriate language tag (e.g. ```python, ```java). NEVER output raw code outside of markdown blocks.{context_str}"
        })
    
    for msg in request.messages:
        if msg.get("role") == "assistant" and msg.get("content", "").startswith("Iniciado. O Specter está online"):
            continue
        history.append(msg)

    if request.mode == 'nim':
        if not request.api_key or not request.api_base:
            raise HTTPException(status_code=400, detail="Faltam as credenciais da API para usar o modo cloud.")
            
        client = OpenAI(
            base_url=request.api_base,
            api_key=request.api_key
        )

    else:
        global local_engine
        path = request.model_id
        if not os.path.exists(path):
            raise HTTPException(status_code=400, detail=f"Ficheiro não encontrado: {path}")
            
        if local_engine["loaded_path"] != path:
            print(f"[Specter] Descarregando motor antigo e a carregar novo modelo em RAM: {path}")
            try:
                local_engine["instance"] = Llama(
                    model_path=path,
                    n_ctx=8192, 
                    n_threads=4,
                    n_gpu_layers=-1,
                    verbose=False
                )
                local_engine["loaded_path"] = path
                print("[Specter] Modelo carregado com sucesso!")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Erro a carregar modelo local: {str(e)}")

    def run_swarm(request: ChatRequest, history: list, active_tools_schema: list):
        clean_history = [msg for msg in history if msg.get("role") != "system"]
        models = request.swarm_models
        if not models:
            msg = {"text": "\\n[ERRO]: Não há modelos configurados no Swarm.\\n"}
            yield f"data: {json.dumps(msg)}\n\n"
            return
            
        manager = models[0]
        
        manager_prompt = """You are the Swarm Manager. The user has given a task.
        You have a team of agents available.
        Analyze the user's task and break it down into sequential sub-tasks.
        For each sub-task, assign it a role (e.g., 'Researcher', 'Coder', 'Reviewer').
        Return the JSON array of objects with 'role' and 'instructions' wrapped in a ```json markdown block.
        Example:
        ```json
        [{"role": "Researcher", "instructions": "Find information about X"}, {"role": "Reviewer", "instructions": "Review the findings."}]
        ```
        """
        
        manager_history = [{"role": "system", "content": manager_prompt}] + clean_history.copy()
        
        msg_switch = {"agent_switch": True, "name": manager.get("name", "Swarm Orchestrator"), "agentRole": "Manager"}
        yield f"data: {json.dumps(msg_switch)}\n\n"
        msg_txt = {"text": "A analisar a tarefa e a distribuir funções pela equipa de agentes...\n"}
        yield f"data: {json.dumps(msg_txt)}\n\n"
        
        manager_plan_str = ""
        try:
            if manager['type'] == 'nim':
                client_mgr = OpenAI(api_key=manager['apiKey'], base_url=manager['apiBase'])
                kwargs = {"model": manager['model'], "messages": manager_history, "stream": True, "temperature": request.temperature, "max_tokens": 4096}
                if manager.get('channelId'):
                    kwargs["extra_body"] = {"channel_id": manager['channelId']}
                stream_res = client_mgr.chat.completions.create(**kwargs)
                if hasattr(stream_res, 'choices'):
                    msg = stream_res.choices[0].message.content
                    if msg:
                        manager_plan_str += msg
                        yield f"data: {json.dumps({'text': msg})}\n\n"
                else:
                    for chunk in stream_res:
                        if not chunk.choices: continue
                        delta = chunk.choices[0].delta
                        if delta.content:
                            manager_plan_str += delta.content
                            yield f"data: {json.dumps({'text': delta.content})}\n\n"
            else:
                global local_engine
                llm = local_engine["instance"]
                if local_engine["loaded_path"] != manager['model']:
                    local_engine["instance"] = Llama(model_path=manager['model'], n_ctx=8192, n_threads=4, n_gpu_layers=-1, verbose=False)
                    local_engine["loaded_path"] = manager['model']
                    llm = local_engine["instance"]
                stream_res = llm.create_chat_completion(messages=manager_history, stream=True)
                for chunk in stream_res:
                    if not chunk.get("choices"): continue
                    delta = chunk["choices"][0]["delta"]
                    if "content" in delta:
                        manager_plan_str += delta["content"]
                        yield f"data: {json.dumps({'text': delta['content']})}\n\n"
        except Exception as e:
            err_msg = f"\\n\\n[ERRO do Manager]: {e}"
            yield f"data: {json.dumps({'text': err_msg})}\n\n"
            return
            
        import re
        try:
            match = re.search(r'\[.*\]', manager_plan_str, re.DOTALL)
            if match:
                plan = json.loads(match.group(0))
            else:
                raise Exception("No JSON array found")
        except Exception as e:
            plan = [{"role": "Agent", "instructions": "Process the user request."}]
            
        plan_msg = f"\nPlano criado com {len(plan)} tarefas.\n"
        yield f"data: {json.dumps({'text': plan_msg})}\n\n"
        
        shared_history = clean_history.copy()
        
        for i, task in enumerate(plan):
            agent = models[(i + 1) % len(models)]
            role_name = task.get('role', 'Agent')
            instructions = task.get('instructions', '')
            
            msg_switch = {"agent_switch": True, "name": agent.get("name", "Local AI"), "agentRole": role_name}
            yield f"data: {json.dumps(msg_switch)}\n\n"
            
            agent_sys_prompt = f"You are acting as: {role_name}. Your specific task is: {instructions}\nReview the conversation history and complete your specific task. Output your thought process clearly."
            agent_history = [{"role": "system", "content": agent_sys_prompt}] + shared_history
            
            full_content = ""
            try:
                if agent['type'] == 'nim':
                    client_agent = OpenAI(api_key=agent['apiKey'], base_url=agent['apiBase'])
                    kwargs = {"model": agent['model'], "messages": agent_history, "stream": True, "temperature": request.temperature, "max_tokens": 4096}
                    if agent.get('channelId'):
                        kwargs["extra_body"] = {"channel_id": agent['channelId']}
                    stream_res = client_agent.chat.completions.create(**kwargs)
                    if hasattr(stream_res, 'choices'):
                        msg = stream_res.choices[0].message.content
                        if msg:
                            full_content += msg
                            yield f"data: {json.dumps({'text': msg})}\\n\\n"
                    else:
                        for chunk in stream_res:
                            if not chunk.choices: continue
                            delta = chunk.choices[0].delta
                            if delta.content:
                                full_content += delta.content
                                yield f"data: {json.dumps({'text': delta.content})}\n\n"
                else:
                    llm = local_engine["instance"]
                    if local_engine["loaded_path"] != agent['model']:
                        local_engine["instance"] = Llama(model_path=agent['model'], n_ctx=8192, n_threads=4, n_gpu_layers=-1, verbose=False)
                        local_engine["loaded_path"] = agent['model']
                        llm = local_engine["instance"]
                    stream_res = llm.create_chat_completion(messages=agent_history, stream=True, temperature=request.temperature)
                    for chunk in stream_res:
                        if not chunk.get("choices"): continue
                        delta = chunk["choices"][0]["delta"]
                        if "content" in delta:
                            full_content += delta["content"]
                            yield f"data: {json.dumps({'text': delta['content']})}\n\n"
            except Exception as e:
                err_msg = f"\\n[ERRO do {role_name}]: {e}"
                yield f"data: {json.dumps({'text': err_msg})}\n\n"
                
            shared_history.append({"role": "assistant", "content": f"[{role_name}]: {full_content}"})
            
        msg_switch = {"agent_switch": True, "name": manager.get("name", "Swarm Orchestrator"), "agentRole": "Synthesis"}
        yield f"data: {json.dumps(msg_switch)}\n\n"
        synth_prompt = "You are the Manager. Review the work done by your team above and provide the final cohesive response to the user. Address the user directly."
        manager_history = [{"role": "system", "content": synth_prompt}] + shared_history
        
        try:
            if manager['type'] == 'nim':
                client_mgr = OpenAI(api_key=manager['apiKey'], base_url=manager['apiBase'])
                kwargs = {"model": manager['model'], "messages": manager_history, "stream": True, "temperature": request.temperature, "max_tokens": 4096}
                if manager.get('channelId'):
                    kwargs["extra_body"] = {"channel_id": manager['channelId']}
                stream_res = client_mgr.chat.completions.create(**kwargs)
                if hasattr(stream_res, 'choices'):
                    msg = stream_res.choices[0].message.content
                    if msg:
                        yield f"data: {json.dumps({'text': msg})}\\n\\n"
                else:
                    for chunk in stream_res:
                        if not chunk.choices: continue
                        delta = chunk.choices[0].delta
                        if delta.content:
                            yield f"data: {json.dumps({'text': delta.content})}\n\n"
            else:
                llm = local_engine["instance"]
                if local_engine["loaded_path"] != manager['model']:
                    local_engine["instance"] = Llama(model_path=manager['model'], n_ctx=8192, n_threads=4, n_gpu_layers=-1, verbose=False)
                    local_engine["loaded_path"] = manager['model']
                    llm = local_engine["instance"]
                stream_res = llm.create_chat_completion(messages=manager_history, stream=True)
                for chunk in stream_res:
                    if not chunk.get("choices"): continue
                    delta = chunk["choices"][0]["delta"]
                    if "content" in delta:
                        yield f"data: {json.dumps({'text': delta['content']})}\n\n"
        except Exception as e:
            err_msg = f"\\n[ERRO na Síntese]: {e}"
            yield f"data: {json.dumps({'text': err_msg})}\n\n"

    def generate_response():
        if request.chat_mode == 'swarm':
            yield from run_swarm(request, history, [])
            return

        full_content = ""
        tool_calls_accumulator = []

        try:
            active_tools_schema = []
            if request.agent_mode:
                if request.terminal_enabled:
                    active_tools_schema.append({
                        "type": "function",
                        "function": {
                            "name": "run_command",
                            "description": "Executes a shell command on the host OS. Highly dangerous. Use only when instructed to manipulate system files or install dependencies.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "command": {"type": "string", "description": "The command string to execute in bash/cmd."}
                                },
                                "required": ["command"]
                            }
                        }
                    })
                for t in tools_schema:
                    name = t["function"]["name"]
                    if name not in loaded_skills:
                        if name not in disabled_skills:
                            active_tools_schema.append(t)
                    else:
                        if name in loadout_skills and name not in disabled_skills:
                            active_tools_schema.append(t)

            def create_chat_completion():
                try:
                    kwargs = {
                        "model": request.model_id,
                        "messages": history,
                        "stream": True,
                        "temperature": request.temperature,
                        "max_tokens": 4096,
                        "tools": active_tools_schema if active_tools_schema else None
                    }
                    if request.channel_id:
                        kwargs["extra_body"] = {"channel_id": request.channel_id}
                        
                    return client.chat.completions.create(**kwargs)
                except Exception as e:
                    return f"Erro na API da OpenAI: {e}"

            if request.mode == 'nim':
                response = create_chat_completion()
                
                if hasattr(response, 'choices'):
                    msg = response.choices[0].message
                    if msg.tool_calls:
                        for tc in msg.tool_calls:
                            tool_calls_accumulator.append({
                                "id": tc.id or "",
                                "type": "function",
                                "function": {"name": tc.function.name or "", "arguments": tc.function.arguments or ""}
                            })
                    if msg.content:
                        full_content += msg.content
                        yield f"data: {json.dumps({'text': msg.content})}\\n\\n"
                else:
                    for chunk in response:
                        if not chunk.choices: continue
                        delta = chunk.choices[0].delta
                        
                        if delta.tool_calls:
                            for tc in delta.tool_calls:
                                if len(tool_calls_accumulator) <= tc.index:
                                    tool_calls_accumulator.append({
                                        "id": tc.id or "",
                                        "type": "function",
                                        "function": {"name": tc.function.name or "", "arguments": ""}
                                    })
                                if tc.function.arguments:
                                    tool_calls_accumulator[tc.index]["function"]["arguments"] += tc.function.arguments
                        
                        if delta.content:
                            full_content += delta.content
                            yield f"data: {json.dumps({'text': delta.content})}\n\n"

                if tool_calls_accumulator:
                    history.append({
                        "role": "assistant",
                        "content": full_content,
                        "tool_calls": tool_calls_accumulator
                    })
                    
                    for tc in tool_calls_accumulator:
                        func_name = tc["function"]["name"]
                        try:
                            func_args = json.loads(tc["function"]["arguments"]) if tc["function"]["arguments"] else {}
                        except json.JSONDecodeError:
                            func_args = {}
                        
                        msg_text = f'\\n\\n> [Usando Skill: {func_name}...]\\n'
                        yield f"data: {json.dumps({'text': msg_text})}\\n\\n"
                        
                        tool_res = execute_tool_call(func_name, func_args)
                        history.append({
                            "role": "tool",
                            "tool_call_id": tc["id"],
                            "name": func_name,
                            "content": str(tool_res)
                        })
                        
                    final_res = client.chat.completions.create(
                        model=request.model_id,
                        messages=history,
                        temperature=request.temperature,
                        max_tokens=4096,
                        stream=True
                    )
                    
                    final_full = ""
                    if hasattr(final_res, 'choices'):
                        msg = final_res.choices[0].message.content
                        if msg:
                            final_full += msg
                            yield f"data: {json.dumps({'text': msg})}\\n\\n"
                    else:
                        for final_chunk in final_res:
                            if not final_chunk.choices: continue
                            d = final_chunk.choices[0].delta
                            if d.content:
                                final_full += d.content
                                yield f"data: {json.dumps({'text': d.content})}\\n\\n"

            else:
                # LOCAL LLAMA_CPP
                llm_local = local_engine["instance"]
                response = llm_local.create_chat_completion(
                    messages=history,
                    stream=True,
                    tools=active_tools_schema if active_tools_schema else None
                )
                
                for chunk in response:
                    if not chunk.get("choices"): continue
                    delta = chunk["choices"][0]["delta"]
                    
                    if "tool_calls" in delta and delta["tool_calls"]:
                        for tc in delta["tool_calls"]:
                            idx = tc.get("index", 0)
                            if len(tool_calls_accumulator) <= idx:
                                tool_calls_accumulator.append({
                                    "id": tc.get("id", ""),
                                    "type": "function",
                                    "function": {"name": tc.get("function", {}).get("name", ""), "arguments": ""}
                                })
                            if "function" in tc and "arguments" in tc["function"]:
                                tool_calls_accumulator[idx]["function"]["arguments"] += tc["function"]["arguments"]
                                
                    if "content" in delta and delta["content"]:
                        full_content += delta["content"]
                        yield f"data: {json.dumps({'text': delta['content']})}\n\n"
                        
                if not tool_calls_accumulator:
                    import re
                    match = re.search(r'```(?:json)?\s*(\{\s*"name"\s*:.*?"arguments"\s*:.*?\})\s*```', full_content, re.DOTALL)
                    if not match:
                        match = re.search(r'^\s*(\{\s*"name"\s*:.*?"arguments"\s*:.*?\})\s*$', full_content, re.DOTALL)
                    if match:
                        try:
                            tc_data = json.loads(match.group(1))
                            if "name" in tc_data and "arguments" in tc_data:
                                tool_calls_accumulator.append({
                                    "id": "call_local_json",
                                    "type": "function",
                                    "function": {
                                        "name": tc_data["name"],
                                        "arguments": json.dumps(tc_data["arguments"]) if isinstance(tc_data["arguments"], dict) else str(tc_data["arguments"])
                                    }
                                })
                        except:
                            pass

                if tool_calls_accumulator:
                    history.append({
                        "role": "assistant",
                        "content": full_content,
                        "tool_calls": tool_calls_accumulator
                    })
                    
                    for tc in tool_calls_accumulator:
                        func_name = tc["function"]["name"]
                        func_args_str = tc["function"]["arguments"]
                        try:
                            func_args = json.loads(func_args_str)
                        except:
                            func_args = {}
                        
                        msg_text = f'\n\n> ⚙️ **Skill ativada autonomamente:** `{func_name}`\n\n'
                        yield f"data: {json.dumps({'text': msg_text})}\n\n"
                        
                        tool_res = execute_tool_call(func_name, func_args)
                        history.append({
                            "role": "tool",
                            "tool_call_id": tc["id"],
                            "name": func_name,
                            "content": str(tool_res)
                        })
                        
                    final_res = llm_local.create_chat_completion(
                        messages=history,
                        temperature=request.temperature,
                        stream=True
                    )
                    
                    for final_chunk in final_res:
                        if not final_chunk.get("choices"): continue
                        d = final_chunk["choices"][0]["delta"]
                        if "content" in d and d["content"]:
                            yield f"data: {json.dumps({'text': d['content']})}\n\n"
                        
        except Exception as e:
            print("Error in generator:", e)
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(generate_response(), media_type="text/event-stream")

@app.post("/api/upload-file")
async def upload_file(file: UploadFile = File(...)):
    try:
        content = await file.read()
        filename = file.filename
        
        if filename.lower().endswith(".pdf"):
            import fitz
            doc = fitz.open(stream=content, filetype="pdf")
            text = f"--- INÍCIO DO PDF: {filename} ---\n\n"
            for page in doc:
                text += page.get_text() + "\n\n"
            text += f"--- FIM DO PDF: {filename} ---"
            return {"filename": filename, "content": text.strip()}
        else:
            text = content.decode("utf-8", errors="replace")
            return {"filename": filename, "content": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
