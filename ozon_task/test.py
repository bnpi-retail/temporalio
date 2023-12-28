from fill_db import (
    connect_to_odoo_api_with_auth,
)

def fill_db_activity() -> None:
    file_path = "./products_from_ozon_api.csv"
    path = "/import/products_from_ozon_api_to_file"
    connect_to_odoo_api_with_auth(
        file_path=file_path,
        path=path,
        username='admin',
        password='admin',
    )

fill_db_activity()