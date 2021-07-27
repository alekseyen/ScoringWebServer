import requests
import pandas as pd


def create_test():
    return pd.read_csv('get_reques_test_data.csv')

host = 'localhost'
port = '500'
url = f'http://{host}:{port}/invocations'
headers = {'Content-Type': 'application/json',}


test = create_test()

# test contains our data from the original train/valid/test split
http_data = test.to_json(orient='split')


r = requests.post(url=url, headers=headers, data=http_data)
print(f'Predictions: {r.text}')
