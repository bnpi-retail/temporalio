import csv
import base64
import requests

from itertools import islice
from secrets import username, password


def connect_to_odoo_api_with_auth(path: str, file_path: str, username: str, password: str):
    url = 'http://0.0.0.0:8070/'
    db = 'db_odoo'
    chunk_size = 1000

    session_url = f'{url}/web/session/authenticate'
    data = {
        'jsonrpc': '2.0',
        'method': 'call',
        'params': {
            'db': db,
            'login': username,
            'password': password,
        }
    }
    session_response = requests.post(session_url, json=data)
    session_data = session_response.json()

    if session_data.get('result') and session_response.cookies.get('session_id'):
        session_id = session_response.cookies['session_id']
    else:
        print(f'Error: Failed to authenticate - {session_data.get("error")}')
        return None

    chunk_size = 1024

    with open(file_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)

        for chunk_count, chunk in enumerate(iter(lambda: list(islice(csv_reader, chunk_size)), []), 1):

            data_to_encode = '\n'.join([','.join(row) for row in chunk])
            encoded_data = base64.b64encode(data_to_encode.encode('utf-8'))
            payload = {'file': ('data.csv', encoded_data)}

            endpoint = f'{url}{path}'
            headers = {'Cookie': f"session_id={session_id}"}
            response = requests.post(endpoint, headers=headers, files=payload)

            print(f"Chunk {chunk_count} sent. Response: {response.text}")

    return "File sent successfully"


connect_to_odoo_api_with_auth('/import/products_from_ozon_api_to_file', './products_from_ozon_api.csv', username, password)
