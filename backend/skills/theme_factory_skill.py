
TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "theme_factory",
        "description": "Baseado no awesome-llm-skills: Produz temas de cor profissionais e consistentes (Hex, RGB) para interfaces baseados numa emoção.",
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "O tópico ou emoção do tema de design (ex: 'oceano', 'cyberpunk')"
                }
            } if True else {},
            "required": ["topic"]
        }
    }
}

def execute(args):
    topic = args.get('topic', '').lower()
    themes = {
        'oceano': {'primary': '#0077b6', 'secondary': '#00b4d8', 'accent': '#90e0ef', 'bg': '#caf0f8'},
        'cyberpunk': {'primary': '#f72585', 'secondary': '#7209b7', 'accent': '#4cc9f0', 'bg': '#0b090a'},
        'natureza': {'primary': '#2d6a4f', 'secondary': '#40916c', 'accent': '#74c69d', 'bg': '#d8f3dc'},
        'default': {'primary': '#333333', 'secondary': '#666666', 'accent': '#e0e0e0', 'bg': '#ffffff'}
    }
    theme = themes.get(topic, themes['default'])
    return f"Design System gerado para '{topic}':\nCor Primária: {theme['primary']}\nCor Secundária: {theme['secondary']}\nCor de Acento: {theme['accent']}\nCor de Fundo: {theme['bg']}"