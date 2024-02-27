from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from workflows import (
        OzonProductsWorkflow,
        OzonFboSupplyOrdersWorkflow,
        OzonTransactionsWorkflow,
        OzonStocksWorkflow,
        OzonPostingsWorkflow,
        OzonActionsWorkflow,
        OzonComputeAllExpensesWorkflow,
        OzonComputeCoefsAndGroupsWorkflow,
        OzonComputePercentExpensesWorkflow,
        OzonTasksWorkflow,
        OzonPricesWorkflow,
        OzonAnalysisWorkflow,
        OzonNumberOfProductsWorkflow,
        CreateMassDataImportWorkflow,
    )


@workflow.defn
class GeneralOzonWorkflow:
    @workflow.run
    async def run(self) -> None:
        await workflow.execute_child_workflow(
            CreateMassDataImportWorkflow.run,
            id="ozon-create-mass-data-import-child-workflow-id",
        )

        await workflow.execute_child_workflow(
            OzonProductsWorkflow.run,
            id="ozon-import-products-child-workflow-id",
        )

        await workflow.execute_child_workflow(
            OzonFboSupplyOrdersWorkflow.run,
            id="ozon-fbo-supply-orders-workflow-id",
        )

        await workflow.execute_child_workflow(
            OzonTransactionsWorkflow.run,
            id="ozon-transactions-workflow-id",
        )

        await workflow.execute_child_workflow(
            OzonStocksWorkflow.run,
            id="ozon-stocks-workflow-id",
        )

        await workflow.execute_child_workflow(
            OzonPostingsWorkflow.run,
            id="ozon-postings-workflow-id",
        )

        await workflow.execute_child_workflow(
            OzonActionsWorkflow.run,
            id="ozon-actions-workflow-id",
        )

        # This place?
        await workflow.execute_child_workflow(
            OzonPricesWorkflow.run,
            id="ozon-price-workflow-id",
        )

        await workflow.execute_child_workflow(
            OzonAnalysisWorkflow.run,
            id="ozon-analysis-workflow-id",
        )

        await workflow.execute_child_workflow(
            OzonNumberOfProductsWorkflow.run,
            id="ozon-number-of-prducst-workflow-id",
        )

        # This place?
        await workflow.execute_child_workflow(
            OzonTasksWorkflow.run,
            id="ozon-tasks-workflow-id",
        )

        await workflow.execute_child_workflow(
            OzonComputePercentExpensesWorkflow.run,
            id="ozon-compute-percent-expenses-workflow-id",
        )

        await workflow.execute_child_workflow(
            OzonComputeCoefsAndGroupsWorkflow.run,
            id="ozon-compute-coef-and-groups-expenses-workflow-id",
        )

        await workflow.execute_child_workflow(
            OzonComputeAllExpensesWorkflow.run,
            id="ozon-compute-all-expenses-workflow-id",
        )



        return