import asyncio
import os
from datetime import timedelta

from temporalio import workflow, activity
from temporalio.client import Client
from temporalio.common import RetryPolicy
from temporalio.worker import Worker

with workflow.unsafe.imports_passed_through():
    from activities import (
        activity_import_transactions_from_period,
        activity_write_transactions_to_odoo,
        activity_remove_csv_files,
    )
    from tools import ImportLogging
    from sentry_interceptor import SentryInterceptor
    from dotenv import load_dotenv
    import sentry_sdk


@activity.defn
async def activity_create_mass_data_import() -> None:
    await ImportLogging().create_mass_data_import({'name': 'Импорт транзакций за период', 'logged_activities_qty': 1})


@workflow.defn
class OzonPostingsForPeriodWorkflow:
    @workflow.run
    async def run(self) -> None:
        await workflow.execute_activity(
            activity_create_mass_data_import,
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=RetryPolicy(maximum_interval=timedelta(minutes=2)),
        )

        await workflow.execute_activity(
            activity_import_transactions_from_period,
            start_to_close_timeout=timedelta(seconds=20000),
            retry_policy=RetryPolicy(maximum_interval=timedelta(hours=24)),
        )

        await workflow.execute_activity(
            activity_write_transactions_to_odoo,
            start_to_close_timeout=timedelta(seconds=20000),
            retry_policy=RetryPolicy(maximum_interval=timedelta(hours=24)),
        )

        await workflow.execute_activity(
            activity_remove_csv_files,
            start_to_close_timeout=timedelta(seconds=20000),
            retry_policy=RetryPolicy(maximum_interval=timedelta(hours=24)),
        )


async def main():
    # Initialize the Sentry SDK
    load_dotenv()
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
    )

    client = await Client.connect("localhost:7233")

    async with Worker(
            client,
            task_queue="ozon-task-queue",
            workflows=[OzonPostingsForPeriodWorkflow],
            activities=[
                activity_create_mass_data_import,
                activity_import_transactions_from_period,
                activity_write_transactions_to_odoo,
                activity_remove_csv_files,
            ],
            interceptors=[SentryInterceptor()],  # Use SentryInterceptor for error reporting
    ):
        handle = await client.start_workflow(
            OzonPostingsForPeriodWorkflow.run,
            id="ozon-workflow-transactions-prev-month-id",
            task_queue="ozon-task-queue",
        )

        await handle.result()


if __name__ == "__main__":
    asyncio.run(main())
