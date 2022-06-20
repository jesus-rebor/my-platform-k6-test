# Running k6 load tests with argo workflows

The easiest way to run the k6 load tests is trough the workflow template created in the
[argo-workflows](https://argo-workflows.infra.internal.shared.empathy.co/workflow-templates/) tool (shared cluster).

To run the test using the workflow template only 3 steps are needed:

1. Locate yourself in the workflows page (the first tab in the left sidebar menu) and select the `k6` option under the _namespace_ field.

2. Click in the `Submit new workflow` button and select the workflow template named as `k6-template`.

3. Fill in the fields with your own values (the _Entrypoint_ option should remain as `<default>`) and in click `Submit`.

   | Field          | Description                                                                                                      |
   | -------------- | ---------------------------------------------------------------------------------------------------------------- |
   | Entrypoint     | Starting point of the workflow. Always should remaing as `<default>`                                             |
   | Team           | Team performing the test                                                                                         |
   | scriptName     | Script used to run the test. It should be previously [uploaded](./upload-script.md) to the efs volume used by k6 |
   | parallelism    | Number of pods used to perform the test                                                                          |
   | k6RunnerImage  | K6 image version                                                                                                 |
   | cpuRequests    | Required amount of cpu for each pod to run                                                                       |
   | cpuLimits      | Maximum amount of cpu for each pod to run                                                                        |
   | memoryRequests | Minimum amount of memory for each pod to run                                                                     |
   | memoryLimits   | Maximum amount of memory for each pod to run                                                                     |

Once triggered, the workflow will automatically start a new pod that will then create the k6 pods that runs the load test.

!!!note  
      After finishing the test, the workflow will also delete all the remaining pods, so the results of the test will be only visible trough the [grafana dashboards](https://grafana.infra.internal.shared.empathy.co/d/CU26nqX7z/k6-loadtest?orgId=1).
