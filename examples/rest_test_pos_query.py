import pandas as pd
import requests

host = "localhost"
port = "5000"
url = f"http://{host}:{port}/"

files = {"file": open("tcs04_example3k.csv", "rb")}

r = requests.post(url=url, files=files)

print(f"result: {r.text}")
