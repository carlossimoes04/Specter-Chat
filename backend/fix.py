import json

with open('main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if 'yield f"data: {json.dumps' in line:
        # Avoid backslashes inside {} of f-string
        # e.g.: yield f"data: {json.dumps({'text': f'\\n\\n[ERRO]: {e}'})}\\n\\n"
        # We need to extract the dict and define it before yield
        import re
        
        # We can just manually replace the problematic f-strings with a safer format
        # but since I know exactly what they are, I can just use a simple string replace
        
        # Fix the literal \\n\\n at the end of the line
        line = line.replace('\\\\n\\\\n"', '\\n\\n"')
        
        # Fix backslashes inside json.dumps({'text': ...})
        # This is a bit tricky with regex, let's just replace the specific strings
        line = line.replace("{'text': '\\n[ERRO]:", "{'text': '\\n[ERRO]:") # Wait, if we just remove the f from the yield string if it doesn't need it?
        
        # Let's just fix the backslashes inside the f-string's {} block.
        # Python <3.12 doesn't allow \ inside {} in f-strings.
        # But wait! If the \ is part of a string literal inside the {}, it's invalid.
        # So: {'text': '\n[ERRO]'} is invalid in an f-string because of \n.
        
        # The easiest fix is to replace `yield f"data: {json.dumps({...})}\n\n"`
        # with `msg = {...}; yield f"data: {json.dumps(msg)}\n\n"`
        pass

# Actually, I will write a script that replaces ALL backslashes inside the f-string curly braces by assigning them to a variable first.
import sys
content = open('main.py', 'r', encoding='utf-8').read()

replacements = [
    (r'yield f"data: {json.dumps({\'text\': \'\\n\[ERRO\]: Não há modelos configurados no Swarm.\\n\'})}\\n\\n"', 
     'msg = {"text": "\\n[ERRO]: Não há modelos configurados no Swarm.\\n"}\n            yield f"data: {json.dumps(msg)}\\n\\n"'),
     
    (r'yield f"data: {json.dumps({\'agent_switch\': True, \'name\': manager.get(\'name\', \'Swarm Orchestrator\'), \'agentRole\': \'Manager\'})}\\n\\n"',
     'msg = {"agent_switch": True, "name": manager.get("name", "Swarm Orchestrator"), "agentRole": "Manager"}\n        yield f"data: {json.dumps(msg)}\\n\\n"'),
     
    (r'yield f"data: {json.dumps({\'text\': \'A analisar a tarefa e a distribuir funções pela equipa de agentes...\\n\'})}\\n\\n"',
     'msg = {"text": "A analisar a tarefa e a distribuir funções pela equipa de agentes...\\n"}\n        yield f"data: {json.dumps(msg)}\\n\\n"'),
     
    (r'yield f"data: {json.dumps({\'text\': delta.content})}\\n\\n"',
     'yield f"data: {json.dumps({\'text\': delta.content})}\\n\\n"'), # Wait, delta.content doesn't have a backslash in the literal! So this is valid syntax!
     
    (r'yield f"data: {json.dumps({\'text\': delta[\'content\']})}\\n\\n"',
     'yield f"data: {json.dumps({\'text\': delta[\'content\']})}\\n\\n"'), # Valid
     
    (r'yield f"data: {json.dumps({\'text\': f\'\\n\\n\[ERRO do Manager\]: {e}\'})}\\n\\n"',
     'err_msg = f"\\n\\n[ERRO do Manager]: {e}"\n            yield f"data: {json.dumps({\'text\': err_msg})}\\n\\n"'),
     
    (r'yield f"data: {json.dumps({\'text\': f\'\\nPlano criado com {len(plan)} tarefas.\\n\'})}\\n\\n"',
     'plan_msg = f"\\nPlano criado com {len(plan)} tarefas.\\n"\n        yield f"data: {json.dumps({\'text\': plan_msg})}\\n\\n"'),
     
    (r'yield f"data: {json.dumps({\'agent_switch\': True, \'name\': agent.get(\'name\', \'Local AI\'), \'agentRole\': role_name})}\\n\\n"',
     'msg_switch = {"agent_switch": True, "name": agent.get("name", "Local AI"), "agentRole": role_name}\n            yield f"data: {json.dumps(msg_switch)}\\n\\n"'),
     
    (r'yield f"data: {json.dumps({\'text\': f\'\\n\[ERRO do {role_name}\]: {e}\'})}\\n\\n"',
     'err_msg = f"\\n[ERRO do {role_name}]: {e}"\n                yield f"data: {json.dumps({\'text\': err_msg})}\\n\\n"'),
     
    (r'yield f"data: {json.dumps({\'agent_switch\': True, \'name\': manager.get(\'name\', \'Swarm Orchestrator\'), \'agentRole\': \'Synthesis\'})}\\n\\n"',
     'msg_switch = {"agent_switch": True, "name": manager.get("name", "Swarm Orchestrator"), "agentRole": "Synthesis"}\n        yield f"data: {json.dumps(msg_switch)}\\n\\n"'),
     
    (r'yield f"data: {json.dumps({\'text\': f\'\\n\[ERRO na Síntese\]: {e}\'})}\\n\\n"',
     'err_msg = f"\\n[ERRO na Síntese]: {e}"\n            yield f"data: {json.dumps({\'text\': err_msg})}\\n\\n"')
]

import re
for old, new in replacements:
    # Need to replace literal \\n\\n" with \n\n" in all matching cases
    # Actually, let\'s just use string replace without regex for simplicity
    pass

# We will just rewrite the python file with regex:
# Find any: yield f"data: {json.dumps({'text': f'\n\n[ERRO...'})}\n\n"
content = re.sub(
    r'yield f"data: \{json\.dumps\(\{\'text\': f\'\\\\n([^<]+)\'\}\)\}\\\\n\\\\n"', 
    r'err_msg = f"\\n\1"\n            yield f"data: {json.dumps({\'text\': err_msg})}\\n\\n"', 
    content
)

content = content.replace('yield f"data: {json.dumps({\'text\': \'\\n[ERRO]: Não há modelos configurados no Swarm.\\n\'})}\\n\\n"',
'msg = {"text": "\\n[ERRO]: Não há modelos configurados no Swarm.\\n"}\n            yield f"data: {json.dumps(msg)}\\n\\n"')

content = content.replace('yield f"data: {json.dumps({\'agent_switch\': True, \'name\': manager.get(\'name\', \'Swarm Orchestrator\'), \'agentRole\': \'Manager\'})}\\n\\n"',
'msg = {"agent_switch": True, "name": manager.get("name", "Swarm Orchestrator"), "agentRole": "Manager"}\n        yield f"data: {json.dumps(msg)}\\n\\n"')

content = content.replace('yield f"data: {json.dumps({\'text\': \'A analisar a tarefa e a distribuir funções pela equipa de agentes...\\n\'})}\\n\\n"',
'msg = {"text": "A analisar a tarefa e a distribuir funções pela equipa de agentes...\\n"}\n        yield f"data: {json.dumps(msg)}\\n\\n"')

content = content.replace('yield f"data: {json.dumps({\'text\': f\'\\n\\n[ERRO do Manager]: {e}\'})}\\n\\n"',
'err_msg = f"\\n\\n[ERRO do Manager]: {e}"\n            yield f"data: {json.dumps({\'text\': err_msg})}\\n\\n"')

content = content.replace('yield f"data: {json.dumps({\'text\': f\'\\nPlano criado com {len(plan)} tarefas.\\n\'})}\\n\\n"',
'plan_msg = f"\\nPlano criado com {len(plan)} tarefas.\\n"\n        yield f"data: {json.dumps({\'text\': plan_msg})}\\n\\n"')

content = content.replace('yield f"data: {json.dumps({\'agent_switch\': True, \'name\': agent.get(\'name\', \'Local AI\'), \'agentRole\': role_name})}\\n\\n"',
'msg_switch = {"agent_switch": True, "name": agent.get("name", "Local AI"), "agentRole": role_name}\n            yield f"data: {json.dumps(msg_switch)}\\n\\n"')

content = content.replace('yield f"data: {json.dumps({\'text\': f\'\\n[ERRO do {role_name}]: {e}\'})}\\n\\n"',
'err_msg = f"\\n[ERRO do {role_name}]: {e}"\n                yield f"data: {json.dumps({\'text\': err_msg})}\\n\\n"')

content = content.replace('yield f"data: {json.dumps({\'agent_switch\': True, \'name\': manager.get(\'name\', \'Swarm Orchestrator\'), \'agentRole\': \'Synthesis\'})}\\n\\n"',
'msg_switch = {"agent_switch": True, "name": manager.get("name", "Swarm Orchestrator"), "agentRole": "Synthesis"}\n        yield f"data: {json.dumps(msg_switch)}\\n\\n"')

content = content.replace('yield f"data: {json.dumps({\'text\': f\'\\n[ERRO na Síntese]: {e}\'})}\\n\\n"',
'err_msg = f"\\n[ERRO na Síntese]: {e}"\n            yield f"data: {json.dumps({\'text\': err_msg})}\\n\\n"')

# Finally, replace all the literal \\n\\n" at the end of these yields to \n\n"
content = content.replace('}\\n\\n"', '}\\n\\n"') # wait, replacing literally `}\n\n"`
# Let's use regex: r'\}\\\\n\\\\n"' to r'}\\n\\n"'
content = re.sub(r'\}\\\\n\\\\n"', r'}\\n\\n"', content)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("done")
