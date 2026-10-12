#!/usr/bin/env python3
"""Quick API connectivity test."""
import urllib.request, json, os

api_key = os.environ.get("DEEPSEEK_API_KEY", "")
print(f"Key length: {len(api_key)}")
print(f"Key prefix: {api_key[:10]}..." if api_key else "NO KEY FOUND!")

url = "https://api.deepseek.com/v1/chat/completions"
payload = json.dumps({
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": "Say hi in 3 words."}],
    "max_tokens": 20
}).encode()
req = urllib.request.Request(url, data=payload, headers={
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
})
try:
    with urllib.request.urlopen(req, timeout=20) as r:
        body = json.loads(r.read())
        print("API OK:", body["choices"][0]["message"]["content"])
except Exception as e:
    print(f"Error: {e}")
