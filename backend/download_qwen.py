import os
from huggingface_hub import hf_hub_download

repo_id = "MrKoN/Huihui-Qwen3.6-35B-A3B-Claude-4.7-Opus-abliterated-Q4_K_M-GGUF"
filename = "huihui-qwen3.6-35b-a3b-claude-4.7-opus-abliterated-q4_k_m.gguf"

print(f"Baixando {filename} do repositório {repo_id}...")
print("Isto pode demorar um bocado dependendo da velocidade da internet.")

model_path = hf_hub_download(
    repo_id=repo_id,
    filename=filename,
    local_dir="models",
    local_dir_use_symlinks=False
)

print(f"Modelo baixado e salvo em: {model_path}")
