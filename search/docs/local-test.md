## Launching a local test

#### Pre-requirements:
* Install python by using `brew install python3`
   * Create a virtual env for storing the project dependencies `python3 -m venv test_env` this will create a folder `test_env` containing 
      a virtual env where we can install the required dependencies. **NOTE:** This directory should not be under version control.
   * Execute `source test_env/bin/activate` and by that way the virtual env will be activated into the current terminal.
   * Install the dependencies:
      - Execute `pip install pipenv`. This will install the tool required for managing the dependencies.
      - Execute `pipenv install` in the directory where the Pipfile is present.
* Install K6 if you don't have it yet.
  * `brew install k6`

> All the following commands must be performed from the root path of the project (`platform-k6-test`).

1. Set up the variables for generating the data in `search/data-generation/options.ini`.
2. Generate the data with `python3 search/data-generation/real-query-generator.py`.
   * The output of this execution will be a JSON file for each endpoint inside `search/generated-data` folder and an
   additional file called `queries.json`.
3. Set up the test variables inside `search/test/test-config.json`.
4. Run the K6 script with `k6 run -e CONFIGURATION_FILE=test-config.json search/test/k6-test-real-data.js`.
   * You can replace the `test-config.json` file with whichever file you need, and even create your own!
