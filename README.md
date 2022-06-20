# K6 load testing

[K6](https://k6.io/docs) provides a simple, flexible and powerful load testing framework. You can use it to test any HTTP API, or any other HTTP-based service. It is designed to be easy to use and easy to extend. It is possible to run load tests from your local machine or from a CI/CD pipeline. It is also possible to run load tests on multiple machines, and to run them in parallel in a distributed manner. There is an [operator](https://github.com/grafana/k6-operator) that can be used to run load tests on Kubernetes clusters.

## Installation

To run your first load test from local, you need to install K6.

```bash
brew install k6
```

Check [this guide](https://k6.io/docs/getting-started/installation/) for more info.

## Running load tests locally

Write your first `script.js` load test.

```js
import http from 'k6/http';
import { sleep } from 'k6';

export default function () {
  http.get('https://test.k6.io');
  sleep(1);
}
```

Finally, run your load test.

```bash
k6 run --vus 10 --duration 30s script.js
```

Check [this guide](https://k6.io/docs/getting-started/running-k6/) for more info.

## Running load tests in a CI/CD pipeline

If you are interested in running your load tests in a CI/CD pipeline, you can check this [tutorial](https://k6.io/blog/load-testing-using-github-actions/) for GitHub Actions or this [tutorial](https://k6.io/blog/getting-started-with-performance-testing-in-ci-cd-using-k6/) for Jenkins.

## Running distributed load tests from Kubernetes

Distributed load tests from kubernetes are managed trough argo-workflows, you can check our [k6 documentation](https://backstage.internal.shared.empathy.co/catalog/default/component/K6-load-testing/docs) to know more about it.

## Adding your own scripts

Each team should have their own folder inside this repository with their custom scripts and config files. Once created the scripts you need upload it to the efs volume in order to perform the tests. You can check [here](https://backstage.internal.shared.empathy.co/catalog/default/component/K6-load-testing/docs/upload-script/) the documentation to upload the scripts.

### Prometheus metrics

The runner container includes an [extension](https://github.com/szkiba/xk6-prometheus) to expose the metrics to Prometheus. The metrics are exposed to the Prometheus server on the metrics port.

You can filter for K6 metrics in [shared Prometheus](https://prometheus.infra.internal.shared.empathy.co/graph) by searching for `k6`.

The metrics are only available when the test is running. Otherwise there will be no metrics.

### Grafana dashboard

There is a Grafana dashboard to check the metrics. The dashboard is available at [shared Grafana](https://grafana.infra.internal.shared.empathy.co/d/CU26nqX7z/k6-loadtest?orgId=1).

## References

- https://www.youtube.com/watch?v=KPyI8rM3LvE
- https://www.youtube.com/watch?v=IJ0uQgn7gI8
- https://github.com/grafana/xk6-kubernetes
- https://k6.io/blog/k6-loves-prometheus/
- https://k6.io/docs/using-k6/options/
- https://k6.io/docs/extensions/guides/build-a-k6-binary-with-extensions/
