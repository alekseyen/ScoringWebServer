import requests
import pandas as pd


def create_test():
    return pd.read_csv('get_reques_test_data.csv')


host = 'localhost'
port = '5000'
url = f'http://{host}:{port}/'

files = {'file': open('tcs04_example3k.csv', 'rb')}

r = requests.post(url=url, files=files)

print(f'result: {r.text}')
