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
    connect_to_odoo_api_with_auth,
    authenticate_to_odoo,
    divide_csv_into_chunks,
    send_csv_file_to_ozon_import_file,
    remove_all_chunk_csv_files,
)

load_dotenv()

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")


@activity.defn
async def ozon_api_activity() -> NoReturn:
    file_path = "./products_from_ozon_api.csv"
    import_products_from_ozon_api_to_file(file_path)


@activity.defn
async def fill_db_activity() -> NoReturn:
    file_path = "./products_from_ozon_api.csv"
    path = "/import/products_from_ozon_api_to_file"
    connect_to_odoo_api_with_auth(
        file_path=file_path,
        path=path,
        username=USERNAME,
        password=PASSWORD,
    )


@activity.defn
async def activity_import_transactions():
    date_from = convert_datetime_str_to_ozon_date(
        str(datetime.combine(datetime.now(), time.min) - timedelta(days=1))
    )
    date_to = convert_datetime_str_to_ozon_date(
        str(datetime.combine(datetime.now(), time.max) - timedelta(days=1))
    )
    file_path = f"./transactions.csv"
    next_page = 1
    while next_page != "Successfully imported all transactions!":
        next_page = import_transactions_from_ozon_api_to_file(
            file_path=file_path, date_from=date_from, date_to=date_to
        )
    return file_path


@activity.defn
async def activity_import_transactions_from_prev_month():
    date_from = convert_datetime_str_to_ozon_date(
        str(datetime.combine(datetime.now(), time.min) - timedelta(days=30))
    )
    date_to = convert_datetime_str_to_ozon_date(
        str(datetime.combine(datetime.now(), time.max) - timedelta(days=1))
    )
    file_path = f"./transactions.csv"
    next_page = 1
    while next_page != "Successfully imported all transactions!":
        next_page = import_transactions_from_ozon_api_to_file(
            file_path=file_path, date_from=date_from, date_to=date_to
        )
    return file_path


@activity.defn
async def activity_write_transactions_to_odoo():
    session_id = authenticate_to_odoo(username=USERNAME, password=PASSWORD)
    file_path = "./transactions.csv"
    divide_csv_into_chunks(file_path)
    url = "http://0.0.0.0:8070/import/transactions_from_ozon_api_to_file"
    try:
        for fpath in os.listdir():
            if fpath.startswith("chunk"):
                send_csv_file_to_ozon_import_file(
                    url=url, session_id=session_id, file_path=fpath
                )
    except Exception as e:
        raise e
    finally:
        remove_all_chunk_csv_files()
        os.remove(file_path)
