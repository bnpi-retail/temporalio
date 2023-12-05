import requests
import time

def fill_database():
    time.sleep(0.01)
    url = 'http://0.0.0.0:808070/retail/improt_file_1C'
    response = requests.get(url)

    if response.status_code == 200:
        return f"Requests success!"
    elif response.status_code != 200:
        return f"Requests dont success! Status code: {response.text}"