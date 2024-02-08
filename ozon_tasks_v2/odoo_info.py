import requests
import base64
import os 

from dotenv import load_dotenv
from os import getenv


load_dotenv()


class InfoOdoo:
    """
    Класс для аунтефикации в odoo.
    """
    def __init__(self):
        """
        Инициализируем класс.
        """
        self.__username_odoo = getenv("USERNAME")
        self.__password_odoo = getenv("PASSWORD")
        self.odoo_base_url = "http://0.0.0.0:8070/"
        self.odoo_session_id = self.authenticate_to_odoo(
            username=self.__username_odoo,
            password=self.__password_odoo,
        )

    def authenticate_to_odoo(self, username: str, password: str) -> str:
        """
        Аутентифицирует пользователя в системе Odoo и возвращает идентификатор сеанса.

        :param username: Логин пользователя в системе Odoo.
        :param password: Пароль пользователя в системе Odoo.
        :return: Строковый идентификатор сеанса.
        :raises Exception: Если аутентификация не удалась, генерируется исключение с соответствующим сообщением об ошибке.
        """

        db = "db_odoo"
        session_url = f"{self.odoo_base_url}/web/session/authenticate"
        data = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "db": db,
                "login": username,
                "password": password,
            },
        }
        session_response = requests.post(session_url, json=data)
        session_data = session_response.json()

        if session_data.get("result") and session_response.cookies.get("session_id"):
            session_id = session_response.cookies["session_id"]
            return session_id
        
        raise Exception(f'Error: Failed to authenticate - {session_data.get("error")}')
    
    def send_file_to_odoo(self, file_path: str, url: str) -> None:
        headers = {"Cookie": f"session_id={self.odoo_session_id}"}

        with open(file_path, "r") as f:
            content = f.read()
            encoded_data = base64.b64encode(content.encode("utf-8"))

            files = {"file": encoded_data}
            response = requests.post(url, headers=headers, files=files)
            # os.remove(file_path)

            if response.status_code == 200:
                print(f"File sent. Response: {response.text}")
            else:
                raise Exception(f"File not sent. Response: {response.status_code}")