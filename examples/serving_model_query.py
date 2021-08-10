import pandas as pd
import requests


def create_test():
    return pd.read_csv("get_reques_test_data.csv")


host = "localhost"  # mn-hdap47.x5.ru
port = "500"
url = f"http://{host}:{port}/invocations"
headers = {
    "Content-Type": "application/json",
}

test = create_test()

http_data = test.to_json(orient="split")

r = requests.post(url=url, headers=headers, data=http_data)
print(f"Predictions: {r.text}")
