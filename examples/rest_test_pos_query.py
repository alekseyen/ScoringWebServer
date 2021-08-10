import json

import pandas as pd
import requests

host = "localhost"  # mn-hdap47.x5.ru
port = "5000"
url = f"http://{host}:{port}/"

params = {"search_type": "optuna"}

files = {"file": open("tcs04_example3k.csv", "rb"), "param": json.dumps(params)}

r = requests.post(url=url, files=files)

print(f"result: {r.text}")
