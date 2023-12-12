import asyncio
import traceback

from datetime import timedelta
from typing import NoReturn

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.common import RetryPolicy
from temporalio.worker import Worker


with workflow.unsafe.imports_passed_through():
    from activities import (
        ozon_api_activity,
        fill_db_activity,
        activity_import_transactions,
        activity_write_transactions_to_odoo,
    )


@workflow.defn
class OzonWorkflow:
    @workflow.run
    async def run(self) -> None:
        await workflow.execute_activity(
            ozon_api_activity,
            start_to_close_timeout=timedelta(seconds=20000),
            retry_policy=RetryPolicy(maximum_interval=timedelta(hours=24)),
        )

        await workflow.execute_activity(
            fill_db_activity,
            start_to_close_timeout=timedelta(seconds=20000),
            retry_policy=RetryPolicy(maximum_interval=timedelta(hours=24)),
        )


@workflow.defn
class OzonTransactionsWorkflow:
    @workflow.run
    async def run(self) -> None:
        await workflow.execute_activity(
            activity_import_transactions,
            start_to_close_timeout=timedelta(seconds=20000),
            retry_policy=RetryPolicy(maximum_interval=timedelta(hours=24)),
        )

        await workflow.execute_activity(
            activity_write_transactions_to_odoo,
            start_to_close_timeout=timedelta(seconds=20000),
            retry_policy=RetryPolicy(maximum_interval=timedelta(hours=24)),
        )


async def main():
    client = await Client.connect("localhost:7233")

    async with Worker(
        client,
        task_queue="ozon-task-queue",
        workflows=[OzonWorkflow],
        activities=[ozon_api_activity, fill_db_activity],
    ):
        handle = await client.start_workflow(
            OzonWorkflow.run,
            id="ozon-workflow-id",
            task_queue="ozon-task-queue",
        )

        await handle.result()

    async with Worker(
        client,
        task_queue="ozon-task-queue",
        workflows=[OzonTransactionsWorkflow],
        activities=[
            activity_import_transactions,
            activity_write_transactions_to_odoo,
        ],
    ):
        handle = await client.start_workflow(
            OzonTransactionsWorkflow.run,
            id="ozon-transactions-workflow",
            task_queue="ozon-task-queue",
        )

        await handle.result()


if __name__ == "__main__":
    asyncio.run(main())
