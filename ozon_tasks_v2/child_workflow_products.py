import asyncio

from datetime import timedelta
from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from activities import (
        get_info_from_odoo,
        get_products_ozon,
        import_products_to_odoo,
    )


@workflow.defn
class ImportProductsChildWorkflow:
    @workflow.run
    async def run(self) -> list:
        file_limit, workers = await workflow.execute_activity(
            get_info_from_odoo, 
            start_to_close_timeout=timedelta(seconds=100000)
        )

        file_paths = await workflow.execute_activity(
            get_products_ozon, file_limit,
            start_to_close_timeout=timedelta(seconds=100000)
        )
        
        chunks = [file_paths[i:i + workers] for i in range(0, len(file_paths), workers)]

        for chunk in chunks:
            async_tasks = [
                workflow.execute_activity(
                    import_products_to_odoo, file_path,
                    start_to_close_timeout=timedelta(seconds=100000)
                )
                for file_path in chunk
            ]
            results = await asyncio.gather(*async_tasks)
        return list(results)
    
