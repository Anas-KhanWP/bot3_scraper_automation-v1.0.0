# 0x4AAAAAAAR0Af-5MfzdbO3p

import requests
import time

api_key = "CAP-B5AF60896E5D3460063F4148663FAD01"  # your api key of capsolver
site_key = "0x4AAAAAAAR0Af-5MfzdbO3p"  # site key of your target site
site_url = "https://www.civitekflorida.com/ocrs/app/search.xhtml"  # page url of your target site

def capsolver():
    payload = {
        "clientKey": api_key,
        "task": {
            "type": 'AntiTurnstileTaskProxyLess',
            "websiteKey": site_key,
            "websiteURL": site_url,
            "metadata": {
                "action": ""  # optional
            }
        }
    }
    res = requests.post("https://api.capsolver.com/createTask", json=payload)
    resp = res.json()
    task_id = resp.get("taskId")
    if not task_id:
        print("Failed to create task:", res.text)
        return
    print(f"Got taskId: {task_id} / Getting result...")

    while True:
        time.sleep(1)  # delay
        payload = {"clientKey": api_key, "taskId": task_id}
        res = requests.post("https://api.capsolver.com/getTaskResult", json=payload)
        resp = res.json()
        status = resp.get("status")
        if status == "ready":
            return resp.get("solution", {}).get('token')
        if status == "failed" or resp.get("errorId"):
            print("Solve failed! response:", res.text)
            return

token = capsolver()
print(token)