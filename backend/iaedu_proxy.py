from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import json
import uuid
import uvicorn
import asyncio

app = FastAPI(title="IAEdu to OpenAI Proxy")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    model = body.get("model", "cmoss7l0f658oko01vk2egfpg")
    messages = body.get("messages", [])
    stream = body.get("stream", False)
    
    # Extract API Key from Authorization header
    auth_header = request.headers.get("Authorization", "")
    api_key = ""
    if auth_header.startswith("Bearer "):
        api_key = auth_header.replace("Bearer ", "").strip()
    
    if not api_key:
        api_key = request.headers.get("x-api-key", "")
        
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing API Key. Please provide it in the Authorization header (Bearer <token>).")

    # Format the entire conversation into a single message context for IAEdu
    formatted_message = ""
    for msg in messages:
        role = msg.get("role", "user").upper()
        content = msg.get("content", "")
        if role == "SYSTEM":
            formatted_message += f"[INSTRUÇÕES DO SISTEMA]: {content}\n\n"
        elif role == "USER":
            formatted_message += f"[UTILIZADOR]: {content}\n\n"
        else:
            formatted_message += f"[ASSISTENTE]: {content}\n\n"
            
    # Prepare IAEdu Request
    # Removing any possible double slashes in the path if they were a typo in the original prompt
    iaedu_endpoint = f"https://api.iaedu.pt/agent-chat/api/v1/agent/{model}/stream"
    
    # Generate a unique ID just for our internal response chunking tracking
    session_id = str(uuid.uuid4())
    
    # O IAEdu exige um channel_id específico que já exista para aquele agente/conta.
    channel_id = body.get("channel_id", "cmp1fijefb030lx01mwi3ef5p")
    data = {
        "channel_id": channel_id,
        "thread_id": str(uuid.uuid4()),
        "user_info": "{}",
        "message": formatted_message.strip()
    }
    
    headers = {
        "x-api-key": api_key
    }

    async def event_generator():
        try:
            async with httpx.AsyncClient() as client:
                async with client.stream("POST", iaedu_endpoint, data=data, headers=headers, timeout=120.0) as response:
                    
                    if response.status_code != 200:
                        error_text = await response.aread()
                        error_msg = f"Error from IAEdu API: {response.status_code} - {error_text.decode('utf-8', errors='ignore')}"
                        yield f"data: {json.dumps({'id': 'error', 'choices': [{'delta': {'content': error_msg}}]})}\n\n"
                        return

                    # Defensive stream reading
                    has_yielded_tokens = False
                    with open("proxy_debug.log", "a", encoding="utf-8") as dbg:
                        dbg.write(f"\\n--- NEW REQUEST to {model} ---\\n")
                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        with open("proxy_debug.log", "a", encoding="utf-8") as dbg:
                            dbg.write(line + "\\n")
                            
                        # Em caso de JSONs colados na mesma linha, separamos
                        line = line.replace("}{", "}\n{")
                        
                        for sub_line in line.split("\n"):
                            sub_line = sub_line.strip()
                            if not sub_line:
                                continue
                                
                            content_to_yield = ""
                            
                            if sub_line.startswith("data:"):
                                raw_data = sub_line[5:].strip()
                            else:
                                raw_data = sub_line
                                
                            if raw_data == "[DONE]":
                                yield "data: [DONE]\n\n"
                                return
                            
                            try:
                                parsed = json.loads(raw_data)
                                if "choices" in parsed:
                                    yield f"data: {json.dumps(parsed)}\n\n"
                                    continue
                                elif "type" in parsed:
                                    # Formato IAEdu
                                    if parsed["type"] == "token":
                                        content_to_yield = parsed.get("content", "")
                                        has_yielded_tokens = True
                                    elif parsed["type"] == "message" and not has_yielded_tokens:
                                        content_to_yield = parsed.get("content", "")
                                    elif parsed["type"] == "context_limit":
                                        content_to_yield = f"\n\n[ERRO DA NUVEM]: O limite de memória (contexto) do IAEdu foi excedido (Usado: {parsed.get('token_pct_used', 100)}%). Por favor, limpa o histórico ou abre um 'Novo Chat'!\n\n"
                                    elif parsed["type"] == "error":
                                        error_reason = parsed.get("content", "Erro desconhecido")
                                        content_to_yield = f"\n\n[ERRO DA NUVEM]: Ocorreu uma interrupção no IAEdu: {error_reason}\n\n"
                                    else:
                                        continue # Ignorar 'start', 'done'
                                elif "text" in parsed:
                                    content_to_yield = parsed["text"]
                            except json.JSONDecodeError:
                                # Apenas emitir se não parecer um json colado mal-formado
                                if "{" not in raw_data:
                                    content_to_yield = raw_data

                            if content_to_yield:
                                chunk_response = {
                                    "id": session_id,
                                    "object": "chat.completion.chunk",
                                    "model": model,
                                    "choices": [
                                        {
                                            "index": 0,
                                            "delta": {"content": content_to_yield},
                                            "finish_reason": None
                                        }
                                    ]
                                }
                                yield f"data: {json.dumps(chunk_response)}\n\n"
                            
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            error_msg = f"\n\n[Erro interno do Proxy: {str(e)}]"
            yield f"data: {json.dumps({'id': 'error', 'choices': [{'delta': {'content': error_msg}}]})}\n\n"
            yield "data: [DONE]\n\n"

    if stream:
        return StreamingResponse(event_generator(), media_type="text/event-stream")
    else:
        try:
            text_result = ""
            async for chunk in event_generator():
                if chunk.startswith("data: ") and chunk.strip() != "data: [DONE]":
                    raw = chunk[6:].strip()
                    try:
                        parsed = json.loads(raw)
                        text_result += parsed.get("choices", [{}])[0].get("delta", {}).get("content", "")
                    except:
                        pass
            
            return {
                "id": session_id,
                "object": "chat.completion",
                "model": model,
                "choices": [
                    {
                        "message": {"role": "assistant", "content": text_result},
                        "finish_reason": "stop"
                    }
                ]
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("iaedu_proxy:app", host="127.0.0.1", port=8001, reload=True)
