## Setting up the data generation

The first step is generating the data that is going to be used on the test. The configuration to specify the data to be
generated is in `search/data-generation/options.ini`. Here is a summary of the parameters needed for that.

| name            | description                                         | example                               |
|-----------------|-----------------------------------------------------|---------------------------------------|
| instance        | the instance to obtain the requests from            | zara                                  |
| languages       | comma-separated languages to obtain the requests of | * es_ES <br> * en_GB,es_ES            |
| endpoints       | comma-separated endpoints to obtain the requests of | * nextqueries <br> * search,empathize |
| generation_mode | the environment target of the requests generated    | * saas <br> * platform                |
| es_host         | the host of the ElasticSearch Logging               |                                       |
| es_user         | the user to access ElasticSearch                    |                                       |
| es_password     | the password to access ElasticSearch                |                                       |


## Setting up the test

After generating the data, the next step is setting up the parameters of the test. In order to ease the process, there
is a file called `search/test/test-config.json` with the parameters needed for most of the tests.

Here's a brief explanation of the parameters contained in that configuration:

| name            | description                                                                                                                  | example                                                                                                                                                                                                                                                                    |
|-----------------|------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| serviceURL      | the base path of the service to be aimed                                                                                     | For platform environment: <br> * https://api.staging.empathy.co/search/v1/query <br> * https://api.empathy.co/search/v1/query <br> For SaaS environment: <br> * https://api-staging.empathybroker.com/search/v1/query <br> * https://api.empathybroker.com/search/v1/query |
| instance        | the instance for whom the test will be launched                                                                              | zara                                                                                                                                                                                                                                                                       |
| endpoints       | the list of the endpoints to throw the test against. <br>  The traffic distribution must be specified in desired percentage. | `{ "name": "search", "trafficDistribution": "30" }`                                                                                                                                                                                                                        |
| tpm             | the target number of transactions per minute                                                                                 | 10000                                                                                                                                                                                                                                                                      |
| rampupTime      | the time to reach the expected tpm                                                                                           | 10m                                                                                                                                                                                                                                                                        |
| holdupTime      | the time to hold the traffic requested after the ramp-up                                                                     | 5m                                                                                                                                                                                                                                                                         |
| preAllocatedVUs | the number of virtual users to be preallocated in the system before launching the test                                       | 300                                                                                                                                                                                                                                                                        |


The test scenario is defined on the `search/test/k6-test-real-data.js`, since K6 requires the configuration for the test to be
defined on a Javascript file.

By default, this test is coded to be a `ramping-arrival-rate`. Nevertheless, this can be changed, so if you want to launch
a load test with a different approach, you can just simply define a new set of scenarios in the `options` constant of
that script.

> Note: these tests require a previous generation of the real data