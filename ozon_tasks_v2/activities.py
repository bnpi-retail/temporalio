from temporalio import activity

from ozon_get_products import (
    OdooMethod, GetProductsFromOzon
)

@activity.defn
async def get_info_from_odoo() -> tuple:
    data = OdooMethod().get_data()
    limit, workers = int(data["limit"]), int(data["workers"])
    return limit, workers


@activity.defn
async def get_products_ozon(file_limit: int) -> list:
    file_paths = GetProductsFromOzon().import_products_from_ozon_api_to_file(
        file_limit=file_limit
    )
    return file_paths


@activity.defn
async def import_products_to_odoo(file_path: str) -> str:
    url = "http://0.0.0.0:8070/import/products_from_ozon_api_to_file"
    methods = OdooMethod()
    methods.send_file_to_odoo(file_path=file_path, url=url)
