## Utilities and monitoring

### Useful commands

* You can check the status of the pods with the command `kubectl get po`.
* To track the memory usage of the pods, you can enter the command `kubectl top pods`.
* To stop the test, you can follow [this guide](argo-workflows.md).

### Monitoring a distributed test

The fancy logs that appear on the console when launching a local test are not a thing when performing a test distributedly.
Instead, we can monitor the status of the test in Grafana.

* [K6-LoadTest](https://grafana.infra.internal.shared.empathy.co/d/CU26nqX7z/k6-loadtest): here you can track the general
status of the test: number of requests performed, number of requests per pod, or number of virtual users, among others.
* [K8S compute resources](https://grafana.infra.internal.shared.empathy.co/d/6581e46e4e5c7ba40a07646395ef7b23/kubernetes-compute-resources-pod):
in this dashboard you can track the memory and CPU consumption of the pods of the tests.
* [Search service](https://grafana.infra.internal.staging.empathy.co/d/asdadwr/search-service-endpoints-and-pods): here is
the information of the search service.
* [CloudFront](https://grafana.infra.internal.shared.empathy.co/d/000000055/cloudfront?orgId=1): here you can monitor
the amount of requests received in total. Mind that not all the requests make it to the search service, since CloudFront
will cache some of them if it's enabled.
* [Staging Platform Kibana](https://kibana-logging.infra.internal.staging.empathy.co/app/discover): here you can check
the logs that the requests are generating.