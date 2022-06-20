# How to upload a new script to the efs volume?

Scripts are uploaded to the efs volume using GitHub actions.
Once you have your teams folder created inside the [platform-k6-tests](https://github.com/empathyco/platform-k6-tests/)
repository you will need to add a GitHub action for your team in the `.github/workflows` folder.

You just need to copy the Github Action below and fill in the <TEAM> values.
This action will upload the files inside your teams folder every time a new commit is pushed to the **main** branch.

You can check [here](https://github.com/empathyco/platform-k6-tests/actions) the logs for all of the workflows.

```yml
on:
  push:
    branches:
      - main
    paths:
      - "<TEAM>/**"
name: Mounting search test files
jobs:
  copy-files:
    name: <TEAM> copy files
    runs-on: [self-hosted, platform]
    steps:
      - uses: actions/checkout@v3
      - name: Create pod with PVC mounted
        uses: steebchen/kubectl@v2.0.0
        with: # defaults to latest kubectl binary version
          config: ${{ secrets.KUBE_CONFIG_DATA }}
          command: apply -f pod.yaml
      - run: sleep 20
      - name: Copy files to pod
        uses: steebchen/kubectl@v2.0.0
        with: # defaults to latest kubectl binary version
          config: ${{ secrets.KUBE_CONFIG_DATA }}
          command: cp ./<TEAM> k6-pvc-copy:/test/ --no-preserve=true
      - run: sleep 10
      - name: Delete pod
        uses: steebchen/kubectl@v2.0.0
        with: # defaults to latest kubectl binary version
          config: ${{ secrets.KUBE_CONFIG_DATA }}
          command: delete pod k6-pvc-copy
```
