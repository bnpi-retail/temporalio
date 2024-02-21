import csv
import base64
import os

from time import sleep

import requests


def authenticate_to_odoo(username: str, password: str):
    """Returns session_id."""

    url = "http://0.0.0.0:8070/"
    db = "db_odoo"
    session_url = f"{url}/web/session/authenticate"
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
    else:
        print(f'Error: Failed to authenticate - {session_data.get("error")}')
        return None


def get_settings_credentials(session_id):
    url = "http://0.0.0.0:8070/get_settings_credentials"
    headers = {"Cookie": f"session_id={session_id}"}
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return {"status_code": response.status_code, "response_text": response.text}


def divide_csv_into_chunks(file_path):
    with open(file_path, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        fieldnames = reader.fieldnames

        for i, row in enumerate(reader):
            if i in range(0, 1000000, 1000):
                name = f"chunk_{i}.csv"
                with open(name, "w") as chunk_csvfile:
                    writer = csv.DictWriter(chunk_csvfile, fieldnames=fieldnames)
                    writer.writeheader()

            with open(name, "a") as chunk_csvfile:
                writer = csv.DictWriter(chunk_csvfile, fieldnames=fieldnames)
                writer.writerow(row)


def send_csv_file_to_ozon_import_file(url, session_id, file_path):
    headers = {"Cookie": f"session_id={session_id}"}
    with open(file_path, "r") as f:
        content = f.read()
        encoded_data = base64.b64encode(content.encode("utf-8"))

        files = {"file": encoded_data}
        response = requests.post(url, headers=headers, files=files)
        print(f"File {file_path} sent. Response: {response.text}")

        return response


def send_all_csv_chunks_to_ozon_import_file(url, session_id):
    for fpath in os.listdir():
        if fpath.startswith("chunk"):
            attempts = 0
            while attempts < 10:
                response = send_csv_file_to_ozon_import_file(
                    url=url, session_id=session_id, file_path=fpath
                )
                if response.status_code == 200:
                    break
                else:
                    sleep(5)
                    attempts += 1


def remove_all_chunk_csv_files():
    for f in os.listdir():
        if f.startswith("chunk"):
            os.remove(f)


def remove_all_csv_files():
    for f in os.listdir():
        if f.endswith(".csv"):
            os.remove(f)