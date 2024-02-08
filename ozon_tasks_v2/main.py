import asyncio

from temporalio import workflow
from temporalio.client import Client
from temporalio.worker import Worker

with workflow.unsafe.imports_passed_through():
    from workflows import (
        OzonGeneralWorkflow,
        ImportProductsChildWorkflow,
    )
    from activities import (
        get_info_from_odoo,
        get_products_ozon,
        import_products_to_odoo,
    )


async def main():
    client = await Client.connect("localhost:7233")

    task_queue = "general-ozon-task-queue"
    unique_id = "general-ozon-workflow-id"

    async with Worker(
        client,
        task_queue=task_queue,
        workflows=[
            OzonGeneralWorkflow, 
            ImportProductsChildWorkflow
        ],
        activities=[
            get_info_from_odoo,
            get_products_ozon, 
            import_products_to_odoo
        ],
    ):

        result = await client.execute_workflow(
            OzonGeneralWorkflow.run,
            id=unique_id,
            task_queue=task_queue,
        )
        print(f"Result: {result}")


if __name__ == "__main__":
    asyncio.run(main())