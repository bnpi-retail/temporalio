from datetime import datetime, time, timedelta, timezone
import os

from ozon_api import (
    import_transactions_from_ozon_api_to_file,
    convert_datetime_str_to_ozon_date_ver2,
)
from fill_db import (
    authenticate_to_odoo,
    divide_csv_into_chunks,
    send_csv_file_to_ozon_import_file,
    remove_all_csv_files,
)

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
TRANSACTIONS_PATH = "./transactions.csv"


string_date_from = "2022-01-01T00:00:00Z"
string_date_to = "2022-01-28T00:00:00Z"
date_from = datetime.fromisoformat(string_date_from)
date_to = datetime.fromisoformat(string_date_to)
today = datetime.now(tz=timezone.utc)
while date_to < today:
    print(f"Transactions from {string_date_from} ---------- to {string_date_to}")
    next_page = 1
    while next_page != "Successfully imported all transactions!":
        next_page = import_transactions_from_ozon_api_to_file(
            file_path=TRANSACTIONS_PATH,
            date_from=string_date_from,
            date_to=string_date_to,
            next_page=next_page,
        )

    date_from = date_to
    date_to = date_to + timedelta(days=28)
    string_date_from = convert_datetime_str_to_ozon_date_ver2(str(date_from))
    string_date_to = convert_datetime_str_to_ozon_date_ver2(str(date_to))


session_id = authenticate_to_odoo(username=USERNAME, password=PASSWORD)
divide_csv_into_chunks(TRANSACTIONS_PATH)
url = "http://0.0.0.0:8070/import/transactions_from_ozon_api_to_file"

for fpath in os.listdir():
    if fpath.startswith("chunk"):
        send_csv_file_to_ozon_import_file(
            url=url, session_id=session_id, file_path=fpath
        )

remove_all_csv_files()
