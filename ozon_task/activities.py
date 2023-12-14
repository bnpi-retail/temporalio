from datetime import datetime, time, timedelta
import os
from typing import NoReturn

from dotenv import load_dotenv

from temporalio import activity
from ozon_api import (
    import_products_from_ozon_api_to_file,
    import_transactions_from_ozon_api_to_file,
    convert_datetime_str_to_ozon_date,
)

from fill_db import (
    authenticate_to_odoo,
    divide_csv_into_chunks,
    send_csv_file_to_ozon_import_file,
    remove_all_csv_files,
)

load_dotenv()

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
TRANSACTIONS_PATH = "./transactions.csv"
PRODUCTS_PATH = "./products.csv"


@activity.defn
async def activity_import_products() -> NoReturn:
    import_products_from_ozon_api_to_file(PRODUCTS_PATH)


@activity.defn
async def activity_write_products_to_odoo():
    session_id = authenticate_to_odoo(username=USERNAME, password=PASSWORD)
    divide_csv_into_chunks(PRODUCTS_PATH)
    url = "http://0.0.0.0:8070/import/products_from_ozon_api_to_file"

    for fpath in os.listdir():
        if fpath.startswith("chunk"):
            send_csv_file_to_ozon_import_file(
                url=url, session_id=session_id, file_path=fpath
            )


@activity.defn
async def activity_import_transactions():
    date_from = convert_datetime_str_to_ozon_date(
        str(datetime.combine(datetime.now(), time.min) - timedelta(days=1))
    )
    date_to = convert_datetime_str_to_ozon_date(
        str(datetime.combine(datetime.now(), time.max) - timedelta(days=1))
    )
    next_page = 1
    while next_page != "Successfully imported all transactions!":
        next_page = import_transactions_from_ozon_api_to_file(
            file_path=TRANSACTIONS_PATH, date_from=date_from, date_to=date_to
        )


@activity.defn
async def activity_import_transactions_from_prev_month():
    date_from = convert_datetime_str_to_ozon_date(
        str(datetime.combine(datetime.now(), time.min) - timedelta(days=30))
    )
    date_to = convert_datetime_str_to_ozon_date(
        str(datetime.combine(datetime.now(), time.max) - timedelta(days=1))
    )
    next_page = 1
    while next_page != "Successfully imported all transactions!":
        next_page = import_transactions_from_ozon_api_to_file(
            file_path=TRANSACTIONS_PATH, date_from=date_from, date_to=date_to
        )


@activity.defn
async def activity_write_transactions_to_odoo():
    session_id = authenticate_to_odoo(username=USERNAME, password=PASSWORD)
    divide_csv_into_chunks(TRANSACTIONS_PATH)
    url = "http://0.0.0.0:8070/import/transactions_from_ozon_api_to_file"

    for fpath in os.listdir():
        if fpath.startswith("chunk"):
            send_csv_file_to_ozon_import_file(
                url=url, session_id=session_id, file_path=fpath
            )


@activity.defn
async def activity_remove_csv_files():
    remove_all_csv_files()
