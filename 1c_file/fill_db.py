import requests

from secrets import username, password


def connect_to_odoo_api_with_auth(path: str, username: str, password: str):
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

    endpoint = f'{url}{path}'
    headers = {'Cookie': f"session_id={session_id}"}
    requests.post(endpoint, headers=headers)

    return "File sent successfully"


connect_to_odoo_api_with_auth('/retail/improt_file_1C', username, password)
