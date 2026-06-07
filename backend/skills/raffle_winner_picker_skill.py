
TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "raffle_winner_picker",
        "description": "Baseado no awesome-llm-skills: Escolhe um vencedor aleatório de forma segura de uma lista de participantes.",
        "parameters": {
            "type": "object",
            "properties": {
                "participants": {
                    "type": "string",
                    "description": "Lista de participantes separados por vírgula"
                }
            } if True else {},
            "required": ["participants"]
        }
    }
}

import random

def execute(args):
    participants = args.get('participants', '')
    if not participants: return "Lista vazia."
    lst = [p.strip() for p in participants.split(',') if p.strip()]
    if not lst: return "Lista vazia."
    winner = random.choice(lst)
    return f"🎉 O vencedor do sorteio é: {winner} (Sorteado entre {len(lst)} participantes)"