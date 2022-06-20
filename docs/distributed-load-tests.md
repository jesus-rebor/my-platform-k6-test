## Running distributed load tests from Kubernetes

!!!warning
    The expected way to run the load tests is using **argo workflows**, you can check the documentation [here](./argo-workflows.md)

The way to run distributed load tests from Kubernetes is to use the [operator](https://github.com/grafana/k6-operator), which is installed in shared cluster with a custom [Helm Chart](https://github.com/empathyco/platform-clusters/tree/main/charts/k6).

The K6 operator includes a controller container that is responsible for managing the load tests. Also includes a CRD (Custom Resource Definition) to extend the Kubernetes API in order to create a custom resource for the load tests. This custom resource is called K6. To execute a test you just need to create a K6 resource and specify the test script. Check the following example:

```yaml
apiVersion: k6.io/v1alpha1
kind: K6
metadata:
  name: k6-sample
spec:
  parallelism: 18
  script:
    localFile: /files/script.js
  arguments: --out prometheus=namespace=k6
  ports:
    - containerPort: 5656
      name: metrics
  runner:
    image: 500449725748.dkr.ecr.eu-west-1.amazonaws.com/ops/k6:v0.1.9
```

Just then apply this file to your cluster.

```sh
kubectl apply -f k6-sample.yaml
```

The runner is a container that runs the load tests. The metrics port is used to expose the metrics. Check the container created in [shared-services repo](https://github.com/empathyco/platform-shared-services/tree/master/applications/k6).

There are 3 ways to mount the script to the container:

- `localFile`: the script is copied to the container and executed.
- `configMap`: the script is read from a config map and executed.
- `volumeClaim`: the script is read from a volume claim and executed.

The first one needs a new container to be created each time the test has changed. The second one has a limitation as there is a character limit of 1048576 bytes to a single configmap so you can't load large files into it.

The last one is a volume claim that is created once and used for all the tests. For that reason an EFS storageClass has been created in shared cluster. As is a distributed test, each runner running in a pod can be scheduled in a different node. To mount the same disk to all the pods, the EFS storage class has been used, the EBS (gp3) storage class can't be used for this purpose.
