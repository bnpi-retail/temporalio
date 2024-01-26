import os

from ozon_api import import_products_from_ozon_api_to_file
from fill_db import (
    authenticate_to_odoo,
    divide_csv_into_chunks,
    send_all_csv_chunks_to_ozon_import_file,
    remove_all_csv_files,
)

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
PRODUCTS_PATH = "./products.csv"
import_products_from_ozon_api_to_file(PRODUCTS_PATH)

session_id = authenticate_to_odoo(username=USERNAME, password=PASSWORD)
divide_csv_into_chunks(PRODUCTS_PATH)
url = "http://0.0.0.0:8070/import/products_from_ozon_api_to_file"
send_all_csv_chunks_to_ozon_import_file(url=url, session_id=session_id)
remove_all_csv_files()
