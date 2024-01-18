import requests

from os import getenv
from dotenv import load_dotenv


load_dotenv()


class AuthOdoo:
    def __init__(self) -> None:
        self.url = 'http://0.0.0.0:8070/'
        self.username = 'admin'
        self.password = 'TyXdcirZQYQp5r7'
        self.db = 'db_odoo'

    def connect_to_odoo_api_with_auth(self) -> dict:
        session_url = f'{self.url}/web/session/authenticate'
        data = {
            'jsonrpc': '2.0',
            'method': 'call',
            'params': {
                'db': self.db,
                'login': self.username,
                'password': self.password,
            }
        }
        session_response = requests.post(session_url, json=data)
        session_data = session_response.json()

        if session_data.get('result') and session_response.cookies.get('session_id'):
            session_id = session_response.cookies['session_id']
            headers = {'Cookie': f"session_id={session_id}"}
            return headers
        else:
            print(f'Error: Failed to authenticate - {session_data.get("error")}')
            return None