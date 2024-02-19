import asyncio
from datetime import timedelta

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.common import RetryPolicy
from temporalio.worker import Worker

with workflow.unsafe.imports_passed_through():
    from get_analysys_data_daily_2_month import OzonAnalysisData
    from tools import odoo_log


@activity.defn
@odoo_log({'name': 'Интерес к продуктам за 65 дней'})
async def ozon_analysis_data_activity():
    return OzonAnalysisData().main()


@workflow.defn
class OzonAnalysisWorkflow:
    @workflow.run
    async def run(self) -> None:
        await workflow.execute_activity(
            ozon_analysis_data_activity,
            start_to_close_timeout=timedelta(seconds=20000),
            retry_policy=RetryPolicy(maximum_interval=timedelta(seconds=24)),
        )


async def main():
    client = await Client.connect("localhost:7233")

    async with Worker(
        client,
        task_queue="ozon-analysis-data-task-queue",
        workflows=[OzonAnalysisWorkflow],
        activities=[
            ozon_analysis_data_activity, 
        ],
    ):

        await client.execute_workflow(
            OzonAnalysisWorkflow.run,
            id="ozon-analysis-data-task-id",
            task_queue="ozon-analysis-data-task-queue",
        )


if __name__ == "__main__":
    asyncio.run(main())
