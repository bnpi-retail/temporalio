import asyncio


from dataclasses import dataclass
from datetime import timedelta

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker


@activity.defn
async def parsing() -> str:
    from ozon_api import import_products_from_ozon_api_to_file
    import_products_from_ozon_api_to_file()
    return f"Success!"


@workflow.defn
class ParsingOzonWorkflow:
    @workflow.run
    async def run(self) -> None:
        result = await workflow.execute_activity(
            parsing,
            start_to_close_timeout=timedelta(seconds=10),
        )
        workflow.logger.info(f"Result: {result}")


async def main():
    client = await Client.connect("localhost:7233")

    async with Worker(
        client,
        task_queue="parsing-ozon-task",
        workflows=[ParsingOzonWorkflow],
        activities=[parsing],
    ):

        print("Running workflow")

        await client.start_workflow(
            ParsingOzonWorkflow.run,
            id="parsing-ozon-task-id",
            task_queue="parsing-ozon-task-queue",
            cron_schedule="0 * * * *",
        )

        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())