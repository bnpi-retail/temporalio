import asyncio

from dataclasses import dataclass
from datetime import timedelta

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker



@dataclass
class ComposeGreetingInput:
    greeting: str
    name: str


@activity.defn
async def compose_greeting(input: ComposeGreetingInput) -> str:
    from ozon_api import import_products_from_ozon_api_to_file
    import_products_from_ozon_api_to_file('./index_local.csv')
    return f"{input.greeting}, {input.name}!"


@workflow.defn
class OzonParsing:
    @workflow.run
    async def run(self, name: str) -> None:
        result = await workflow.execute_activity(
            compose_greeting,
            ComposeGreetingInput("Hello", name),
            start_to_close_timeout=timedelta(seconds=500),
        )
        workflow.logger.info("Result: %s", result)


async def main():
    client = await Client.connect("localhost:7233")

    async with Worker(
        client,
        task_queue="ozon-parsing-task-queue",
        workflows=[OzonParsing],
        activities=[compose_greeting],
    ):

        print("Running workflow once a minute")

        await client.start_workflow(
            OzonParsing.run,
            "World",
            id="ozon-parsing-task-id",
            task_queue="ozon-parsing-task-queue",
            cron_schedule = "0 0 * * *",
        )

        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())