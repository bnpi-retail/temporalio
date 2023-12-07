import requests
from secrets import username, password


def connect_to_odoo_api_with_auth(path: str):
    url = 'http://0.0.0.0:8070/'
    db = 'db_odoo'

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

    url = 'http://0.0.0.0:8070/'
    endpoint = f'{url}{path}'

    response = requests.post(endpoint, 
                                headers={'Content-Type': 'application/json',
                                        'Cookie': f"session_id={session_id}"})
    print(response.text)
    return response.status_code
