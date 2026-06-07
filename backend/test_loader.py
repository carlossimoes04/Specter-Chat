import os
import glob
import sys
import importlib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SKILLS_DIR = os.path.join(BASE_DIR, "skills")
sys.path.append(SKILLS_DIR)

print("Procurando em:", SKILLS_DIR)
files = glob.glob(os.path.join(SKILLS_DIR, "*.py"))
print("Ficheiros encontrados:", files)

for file in files:
    if file.endswith("__init__.py"): continue
    module_name = os.path.basename(file)[:-3]
    try:
        mod = importlib.import_module(module_name)
        print("SUCESSO:", module_name)
    except Exception as e:
        print("ERRO:", module_name, "->", e)
