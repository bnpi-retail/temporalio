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
    from fill_db import fill_database
    status = fill_database()
    print(status)
    return f"{input.greeting}, {input.name}!"


@workflow.defn
class GreetingWorkflow:
    @workflow.run
    async def run(self, name: str) -> None:
        result = await workflow.execute_activity(
            compose_greeting,
            ComposeGreetingInput("Hello", name),
            start_to_close_timeout=timedelta(seconds=10),
        )
        workflow.logger.info("Result: %s", result)


async def main():
    client = await Client.connect("localhost:7233")

    async with Worker(
        client,
        task_queue="hello-cron-task-queue",
        workflows=[GreetingWorkflow],
        activities=[compose_greeting],
    ):

        print("Running workflow once a minute")

        await client.start_workflow(
            GreetingWorkflow.run,
            "World",
            id="fill-db-cron-workflow-id",
            task_queue="hello-cron-task-queue",
            cron_schedule="* * * * *",
        )

        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())