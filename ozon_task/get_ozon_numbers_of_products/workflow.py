import asyncio
import traceback
import ast

from datetime import timedelta
from typing import NoReturn

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.common import RetryPolicy
from temporalio.worker import Worker

with workflow.unsafe.imports_passed_through():
    from get_ozon_numbers_of_products import OzonNumberOfProducts


@activity.defn
async def get_ozon_number_of_products() -> NoReturn:
    OzonNumberOfProducts().main()

@workflow.defn
class OzonNumberOfProductsWorkflow:
    @workflow.run
    async def run(self) -> None:
        await workflow.execute_activity(
            get_ozon_number_of_products,
            start_to_close_timeout=timedelta(seconds=20000),
            retry_policy=RetryPolicy(maximum_interval=timedelta(hours=24)),
        )

async def main():
    client = await Client.connect("localhost:7233")

    async with Worker(
        client,
        task_queue="ozon-number-of-products-task-queue",
        workflows=[OzonNumberOfProductsWorkflow],
        activities=[
            get_ozon_number_of_products, 
        ],
    ):

        await client.execute_workflow(
            OzonNumberOfProductsWorkflow.run,
            id="ozon-number-of-products-task-id",
            task_queue="ozon-number-of-products-task-queue",
        )


if __name__ == "__main__":
    asyncio.run(main())
