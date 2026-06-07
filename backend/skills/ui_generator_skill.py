import os
import time

# Cria a pasta de mockups se não existir
os.makedirs("data/ui_mockups", exist_ok=True)

TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "generate_ui_mockup",
        "description": "Gera código HTML com TailwindCSS para criar componentes de UI baseados no design requisitado e guarda num ficheiro HTML local para o utilizador visualizar.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "Nome do ficheiro a guardar (ex: 'login_page', 'dashboard'). Não incluir .html."
                },
                "html_code": {
                    "type": "string",
                    "description": "O código completo em HTML contendo a estrutura e classes do TailwindCSS (via CDN) para renderizar a página/componente."
                }
            },
            "required": ["filename", "html_code"]
        }
    }
}

def execute(args):
    try:
        filename = args.get("filename", f"ui_{int(time.time())}")
        html_code = args.get("html_code", "")
        
        # Garante que o código tem a framework Tailwind
        if "<script src=\"https://cdn.tailwindcss.com\"></script>" not in html_code:
            if "<head>" in html_code:
                html_code = html_code.replace("<head>", "<head>\n<script src=\"https://cdn.tailwindcss.com\"></script>")
            else:
                html_code = f"<!DOCTYPE html><html><head><script src=\"https://cdn.tailwindcss.com\"></script></head><body class='bg-gray-100 p-8'>\n{html_code}\n</body></html>"
        
        filepath = os.path.abspath(f"data/ui_mockups/{filename}.html")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_code)
            
        return f"Sucesso! O teu Design de UI foi gerado e guardado localmente.\nPodes abri-lo no browser com o caminho: file:///{filepath.replace(chr(92), '/')}"
    except Exception as e:
        return f"Erro ao gerar UI: {e}"
