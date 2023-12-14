import asyncio
from datetime import timedelta

from temporalio import workflow
from temporalio.client import Client
from temporalio.common import RetryPolicy
from temporalio.worker import Worker


with workflow.unsafe.imports_passed_through():
    from activities import (
        activity_import_stocks,
        activity_write_stocks_to_odoo,
        activity_remove_csv_files,
    )


@workflow.defn
class OzonStocksWorkflow:
    @workflow.run
    async def run(self) -> None:
        await workflow.execute_activity(
            activity_import_stocks,
            start_to_close_timeout=timedelta(seconds=20000),
            retry_policy=RetryPolicy(maximum_interval=timedelta(hours=24)),
        )

        await workflow.execute_activity(
            activity_write_stocks_to_odoo,
            start_to_close_timeout=timedelta(seconds=20000),
            retry_policy=RetryPolicy(maximum_interval=timedelta(hours=24)),
        )

        await workflow.execute_activity(
            activity_remove_csv_files,
            start_to_close_timeout=timedelta(seconds=20000),
            retry_policy=RetryPolicy(maximum_interval=timedelta(hours=24)),
        )


async def main():
    client = await Client.connect("localhost:7233")

    async with Worker(
        client,
        task_queue="ozon-task-queue",
        workflows=[OzonStocksWorkflow],
        activities=[
            activity_import_stocks,
            activity_write_stocks_to_odoo,
            activity_remove_csv_files,
        ],
    ):
        handle = await client.start_workflow(
            OzonStocksWorkflow.run,
            id="ozon-transactions-workflow",
            task_queue="ozon-task-queue",
        )

        await handle.result()


if __name__ == "__main__":
    asyncio.run(main())
