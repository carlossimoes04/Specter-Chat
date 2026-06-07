import os
from huggingface_hub import hf_hub_download

# Repositório e ficheiro do modelo a baixar (Phi-3-mini, muito rápido em CPU e bom para testes)
repo_id = "bartowski/Phi-3-mini-4k-instruct-v0.3-GGUF"
filename = "Phi-3-mini-4k-instruct-v0.3-Q4_K_M.gguf"

print(f"Baixando {filename} do repositório {repo_id}...")
print("Isto pode demorar alguns minutos dependendo da sua internet (tamanho ~2.4 GB).")

# Baixar o modelo para a pasta 'models' dentro de backend
model_path = hf_hub_download(
    repo_id=repo_id,
    filename=filename,
    local_dir="models",
    local_dir_use_symlinks=False
)

print(f"Modelo baixado e salvo em: {model_path}")
