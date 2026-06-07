import os
import glob

skills_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skills")

for file in glob.glob(os.path.join(skills_dir, "*.py")):
    with open(file, "r", encoding="utf-8") as f:
        content = f.read()
    
    if "if true else" in content:
        content = content.replace("if true else", "if True else")
        with open(file, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Corrigido: {os.path.basename(file)}")
