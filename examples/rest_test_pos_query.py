import json

import pandas as pd
import requests

host = "0.0.0.0"  # mn-hdap47.x5.ru
port = "5000"
url = f"http://{host}:{port}/send_csv"

params = {"search_type": "single"}

files = {"file": open("tcs04_example3k.csv", "rb"), "param": json.dumps(params)}

r = requests.post(url=url, files=files)

print(f"result: {r.text}")
