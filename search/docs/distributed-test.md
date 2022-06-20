## Launching a distributed test

#### Pre-requirements:
* Python requirements from the local execution steps.
* The test is launched inside the shared environment, so you have to configure the `shared-services` cluster in your
machine. In [this URL](https://rancher.internal.ops.empathy.co/dashboard/c/c-55czg) you have the cluster in Rancher,
download the KubeConfig and add it to your `~/.kube/config` file.

> All the following commands must be performed from the root path of the project (`platform-k6-test`).

The setup of the distributed test follow the same steps as the local execution:
1. Set up the variables for generating the data in `search/data-generation/options.ini`.
2. Generate the data with `python3 search/data-generation/real-query-generator.py`.
3. Set up the test variables inside `search/test/test-config.json`.
4. Commit the files to be included in the test to a new branch and create a pull request.
5. When the pull request is merged, a Github Action is triggered to copy the files inside the pod that will launch the test.
You can track the progress in [here](https://github.com/empathyco/platform-k6-tests/actions/workflows/search.yml).
6. Once the files are copied successfully, just submit a new workflow following [this guide](argo-workflows.md).