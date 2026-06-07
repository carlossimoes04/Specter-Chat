import urllib.request
import json
import base64

try:
    req = urllib.request.Request('https://api.github.com/repos/Prat011/awesome-llm-skills/readme', headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode('utf-8'))
        text = base64.b64decode(data['content']).decode('utf-8')
        with open('readme.md', 'w', encoding='utf-8') as f:
            f.write(text)

except Exception as e:
    print(e)
