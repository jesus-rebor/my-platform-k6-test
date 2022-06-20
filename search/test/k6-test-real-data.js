import http from 'k6/http';
import {
	SharedArray
} from 'k6/data';

const ROOT_PATH = "."

//Configuration constants
const CONFIGURATION = JSON.parse(open(ROOT_PATH + `/${__ENV.CONFIGURATION_FILE}`));
const SERVICE_URL = CONFIGURATION.serviceConfiguration.serviceURL;

//We obtain the list of endpoints available to throw the requests at.
//In the configuration we set up the percentage of traffic desired, but
//the way that this works internally is by setting up ranges for the
//different types of requests that we can have.
const ENDPOINTS = new SharedArray("endpoints-configuration", function() {
  let endpointList = CONFIGURATION.clientConfiguration.endpoints;
  endpointList.forEach(e => {
        let index = endpointList.findIndex(self => self.name == e.name);
        let percentage = 0;
        if (index-1 >= 0) {
            percentage += Number(endpointList[index-1].trafficDistribution);
        }
        percentage += Number(e.trafficDistribution);
        if(percentage > 100) {
            throw new Error("[ERROR] The sum of the trafficDistribution percentages must be lower or equal to 100.");
        }
        e.trafficDistribution = percentage;
  });
  return endpointList;
});

//Setting up the local path where the files are stored, since it varies between local and distributed environments
const LOCAL_PATH = "/../generated-data";


//Load dataset
const DATASET = createDataset();

function createDataset () {
  let data = [];
  //We are loading the data for all the endpoints specified on the configuration
  ENDPOINTS.forEach(endpoint =>
    data.push(new SharedArray(endpoint.name, function() {
        return JSON.parse(open(ROOT_PATH + LOCAL_PATH + '/' + endpoint.name + '-real-data.json'));
    }))
  );
  return data;
}

const QUERIES = new SharedArray("queries", function() {
  return JSON.parse(open(ROOT_PATH + LOCAL_PATH + '/queries.json'));
})[0];

// Test definition
export const options = {
	summaryTimeUnit: 'ms',
	discardResponseBodies: true,
	scenarios: {
		contacts: {
			executor: 'ramping-arrival-rate',
			startRate: 1,
			timeUnit: '1m',
			maxVUs: 30000,
			preAllocatedVUs: CONFIGURATION.testConfiguration.preAllocatedVUs,
			stages: [{
					target: CONFIGURATION.testConfiguration.tpm,
					duration: CONFIGURATION.testConfiguration.rampupTime
				},
				{
					target: CONFIGURATION.testConfiguration.tpm,
					duration: CONFIGURATION.testConfiguration.holdupTime
				} //hold up
			],
		}
	}
};

const params = {
    headers: {
      'User-Agent': 'loadtest',
    },
};

export default function () {
    var num = Math.random()*100;

    //We obtain to which endpoint must the request point at
    let endpoint = "";
    ENDPOINTS.forEach(e => {
        if (endpoint == "" && num <= e.trafficDistribution) {
            endpoint = e.name;
        }
    });

    //We obtain the index of the endpoint inside the array of endpoints
    let endpointIndex = ENDPOINTS.findIndex(e => e.name == endpoint);

    //We obtain a random path from the dataset for that endpoint
    let dataset = DATASET[endpointIndex];
    let path = dataset[Math.floor(Math.random() * dataset.length)].path;

    //From the path, we obtain the language
    let lang_match = path.match(/lang=.*?&/);

    if (lang_match) {
      let lang = lang_match[0].replace("lang=", "").replace("&", "")

      //We get the queries for that language and replace it into the path
      let langQueries = QUERIES[lang];
      path = path.replace("${QUERY}", langQueries[Math.floor(Math.random() * langQueries.length)]);
    }
    //We concatenate all the needed parts to have a working url
    let url = [SERVICE_URL, path].join("/");

    //We perform the request
    http.get(url, params);
}

