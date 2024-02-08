from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from child_workflow_products import (
        ImportProductsChildWorkflow,
    )


@workflow.defn
class OzonGeneralWorkflow:
    @workflow.run
    async def run(self) -> None:
        await workflow.execute_child_workflow(
            ImportProductsChildWorkflow.run,
            id="ozon-import-products-child-workflow",
        )
        return
