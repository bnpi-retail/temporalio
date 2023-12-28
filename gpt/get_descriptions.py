import requests

from os import getenv
from dotenv import load_dotenv


load_dotenv()


class GetDescriptions:
    def __init__(self):
        self.session = requests.Session()
        self.token = getenv("DJANGO_TOKEN")

    def get_description(self):
        url = 'http://0.0.0.0:8000/take-description-from-odoo/'
        api_token_value = self.token

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Token {api_token_value}',
        }

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return None
        
        res = response.json()
        # print(f'get_description {res}')
        id = res.get('id')
        desscription = res.get('desscription')
        return id, desscription

    def take_request_to_gpt(self, message: str):
        url = 'http://0.0.0.0:8000/take-request-to-gpt/'
        api_token_value = self.token

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Token {api_token_value}',
        }
        payload = {'text': message}
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            return None

        res = response.json()
        # print(f'take_request_to_gpt {res}')
        answers = res.get('answer')[0][1]
        answers = answers.split('#')
        for answer in answers:
            answer.replace('\n', '').replace(';', '')
        print(answers[1:])
        return answers[1:]

    def send_to_odoo(self, id: int, message) -> int:
        url = 'http://0.0.0.0:8000/send-to-odoo/'
        api_token_value = self.token

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Token {api_token_value}',
        }

        payload = {'id': id, 'message': message}
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            return None
        
        res = response.json()
        print(f'send_to_odoo {res}')
        desscription = res.get('desscription')
        return desscription

    def main(self):
        id, description = self.get_description()
        if not description: 
            print('Не удалось получить описание товара!')
            return 

        answer = self.take_request_to_gpt(description)
        if not answer: 
            print('Не удалось получить поисковые запросы!')
            return 

        self.send_to_odoo(id, answer)

GetDescriptions().main()