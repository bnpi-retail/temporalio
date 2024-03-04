import asyncio
from datetime import timedelta

from temporalio import workflow, activity
from temporalio.client import Client
from temporalio.common import RetryPolicy
from temporalio.worker import Worker


with workflow.unsafe.imports_passed_through():
    from activities import (
        activity_import_postings_40_days,
        activity_write_postings_to_odoo,
        activity_remove_csv_files,
    )
    from tools import ImportLogging, odoo_log

@activity.defn
async def activity_create_mass_data_import() -> None:
    await ImportLogging().create_mass_data_import({'name': 'Импорт отправлений за период', 'logged_activities_qty': 1})


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
            activity_import_postings_40_days,
            start_to_close_timeout=timedelta(seconds=20000),
            retry_policy=RetryPolicy(maximum_interval=timedelta(hours=24)),
        )

        await workflow.execute_activity(
            activity_write_postings_to_odoo,
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
        workflows=[OzonPostingsForPeriodWorkflow],
        activities=[
            activity_create_mass_data_import,
            activity_import_postings_40_days,
            activity_write_postings_to_odoo,
            activity_remove_csv_files,
        ],
    ):
        handle = await client.start_workflow(
            OzonPostingsForPeriodWorkflow.run,
            id="ozon-workflow-transactions-prev-month-id",
            task_queue="ozon-task-queue",
        )

        await handle.result()


if __name__ == "__main__":
    asyncio.run(main())
