import socket

TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "check_domain_availability",
        "description": "Skill baseada no 'Domain Name Brainstormer' do awesome-llm-skills: Verifica de forma rápida se um domínio de internet já está a ser utilizado (através de resolução DNS).",
        "parameters": {
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "O domínio que queres verificar (ex: 'meuprojetofixe.com', 'startup.ai')"
                }
            },
            "required": ["domain"]
        }
    }
}

def execute(args):
    domain = args.get("domain", "").strip()
    if not domain:
        return "Erro: Tens de fornecer o nome do domínio."
        
    try:
        socket.gethostbyname(domain)
        return f"❌ Domínio INDISPONÍVEL: O domínio '{domain}' já está registado e ativo no DNS."
    except socket.gaierror:
        return f"✅ Domínio POTENCIALMENTE DISPONÍVEL: O domínio '{domain}' não tem registos de DNS ativos. Grande probabilidade de estar livre para compra!"
    except Exception as e:
        return f"Erro na verificação do domínio '{domain}': {e}"
