import os

from ozon_api import import_stocks_from_ozon_api_to_file
from fill_db import (
    authenticate_to_odoo,
    divide_csv_into_chunks,
    send_all_csv_chunks_to_ozon_import_file,
    remove_all_csv_files,
)

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
STOCKS_PATH = "./stocks.csv"
import_stocks_from_ozon_api_to_file(STOCKS_PATH)

session_id = authenticate_to_odoo(username=USERNAME, password=PASSWORD)
divide_csv_into_chunks(STOCKS_PATH)
url = "http://0.0.0.0:8070/import/stocks_from_ozon_api_to_file"

send_all_csv_chunks_to_ozon_import_file(url=url, session_id=session_id)
remove_all_csv_files()
