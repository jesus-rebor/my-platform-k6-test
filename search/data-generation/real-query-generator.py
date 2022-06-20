import configparser
import datetime
import json
import logging
import os
import pathlib
import re
import urllib.parse
from collections import defaultdict
from datetime import timedelta
from elasticsearch import Elasticsearch

# Configuration
ENDPOINTS = []
ALLOWED_GENERATION_MODES = ["saas", "platform"]
MAX_ITERATIONS = 4
INSTANCES = ""
LANGUAGES = ""
GENERATION_MODE = ""

# ElasticSearch logging configuration
ES_HOST = ""
ES_USER = ""
ES_PASSWORD = ""

es = {}
ROOT_DIR = str(pathlib.Path().resolve()) + "/search"

NOW_TIMESTAMP_MS = datetime.datetime.now()
START_TIMESTAMP_MS = NOW_TIMESTAMP_MS - timedelta(days=1)


def get_raw_data(endpoint: str, iteration):
    start = START_TIMESTAMP_MS - timedelta(days=iteration)
    end = NOW_TIMESTAMP_MS - timedelta(days=iteration)

    body = {
        "size": 1000,
        "query": {
            "bool": {
                "must": [
                    {"term": {"x_host_header": "api.empathybroker.com"}},
                    get_term_query(),
                    {"term": {"sc_status": "200"}},
                    {"term": {"empathy.endpoint": endpoint}},
                    {
                        "range": {
                            "@timestamp": {
                                "gte": start.strftime('%Y-%m-%d %H:%M:%S'),
                                "lte": end.strftime('%Y-%m-%d %H:%M:%S'),
                                "format": "yyyy-MM-dd HH:mm:ss"
                            }
                        }
                    }
                ],
                "filter": [],
                "must_not": []
            }
        },
        "fields": [
            "cs_uri_query",
            "empathy.endpoint",
            "empathy.customer",
            "empathy.query_params.lang"
        ],
        "_source": "false"
    }

    return es.search(body=body, index="aws-cloudfront-*", request_timeout=60)


def get_term_query():
    if len(INSTANCES) > 0:
        return {"terms": {"empathy.customer": INSTANCES}}
    else:
        return {"term": {"empathy.customer": INSTANCES[0]}}


def append_samples_to_data_set_files(raw_data: dict):
    json_array = []
    queries = defaultdict(list)
    for entry in raw_data["hits"]["hits"]:
        source = entry.get("fields", "")
        path = ''.join(source.get("cs_uri_query", ""))
        data_set = '/'.join(source.get("empathy.customer", []) + source.get("empathy.endpoint", []))
        real_url = data_set + "?" + path

        # Request transformation
        tuned_url = initial_transformations(real_url)

        # We extract the actual query from the request
        (query, tuned_url) = extract_query(tuned_url)

        if GENERATION_MODE == "platform":
            tuned_url = transform_request_to_platform(tuned_url)

        row = {
            'path': tuned_url
        }

        lang_param = source.get("empathy.query_params.lang")
        query_lang = ""
        if lang_param is not None:
            query_lang = source.get("empathy.query_params.lang")[0]
        # we skip the hits that do not contain the desired languages
        if query_lang in LANGUAGES:
            json_array.append(row)
            if query:
                queries[query_lang].append(query)

    return json_array, queries


def extract_query(tuned_url):
    query = ''
    q = re.search("q=[^&]*", tuned_url)
    if q:
        query = q.group(0)[2:]
        tuned_url = re.sub('q=[^&]*', 'q=${QUERY}&', tuned_url)

    return query, tuned_url


def initial_transformations(tuned_url):
    tuned_url = re.sub('jsonCallback=_pdJsonpCallback_[0-9]*&', '&', tuned_url)
    tuned_url = urllib.parse.unquote_plus(tuned_url)
    tuned_url = tuned_url.replace("filter=&", "")
    tuned_url = tuned_url.replace("sectionName%3A", "sectionName:")
    tuned_url = tuned_url.replace("searchSection%3A", "searchSection:")
    tuned_url = re.sub('o=json', '', tuned_url)
    tuned_url = re.sub('m=[0-9]*', '', tuned_url)
    tuned_url = tuned_url.replace(" ", "%20")
    tuned_url = re.sub('equalize=*', '', tuned_url)
    tuned_url = re.sub('catalogue=*&', 'catalogue=', tuned_url)
    return tuned_url


def transform_request_to_platform(tuned_url):
    tuned_url = tuned_url.replace("q=", "query=")
    tuned_url = tuned_url.replace("sort=score", "sort=_score")
    tuned_url = re.sub('sort=kpi_salesAmount_[0-9]*%20desc&', '', tuned_url)
    tuned_url = tuned_url.replace("filter=searchSection:%22WOMAN%22%20OR%20searchSection:%22ALL%22",
                                  "filter=searchSection:WOMAN&filter=searchSection:ALL")
    tuned_url = tuned_url.replace("filter=searchSection:%22MAN%22%20OR%20searchSection:%22ALL%22",
                                  "filter=searchSection:MAN&filter=searchSection:ALL")
    tuned_url = tuned_url.replace("filter=searchSection:%22KID%22%20OR%20searchSection:%22ALL%22",
                                  "filter=searchSection:KID&filter=searchSection:ALL")
    tuned_url = tuned_url.replace("filter=searchSection:%22HOME%22%20OR%20searchSection:%22ALL%22",
                                  "filter=searchSection:HOME&filter=searchSection:ALL")
    tuned_url = tuned_url.replace("filter=sectionName:%22WOMAN%22%20OR%20sectionName:%22ALL%22",
                                  "filter=sectionName:WOMAN&filter=sectionName:ALL")
    tuned_url = tuned_url.replace("filter=sectionName:\"WOMAN\"%20OR%20sectionName:\"ALL\"",
                                  "filter=sectionName:WOMAN&filter=sectionName:ALL")
    tuned_url = tuned_url.replace("filter=sectionName:%22MAN%22%20OR%20sectionName:%22ALL%22",
                                  "filter=sectionName:MAN&filter=sectionName:ALL")
    tuned_url = tuned_url.replace("filter=sectionName:\"MAN\"%20OR%20sectionName:\"ALL\"",
                                  "filter=sectionName:MAN&filter=sectionName:ALL")
    tuned_url = tuned_url.replace("filter=sectionName:%22KID%22%20OR%20sectionName:%22ALL%22",
                                  "filter=sectionName:KID&filter=sectionName:ALL")
    tuned_url = tuned_url.replace("filter=sectionName:%22HOME%22%20OR%20sectionName:%22ALL%22",
                                  "filter=sectionName:HOME&filter=sectionName:ALL")
    tuned_url = tuned_url.replace("autocomplete", "empathize")

    # In empathize, the field _score is called weight
    if "empathize?" in tuned_url:
        tuned_url = tuned_url.replace("sort=_score", "sort=weight")
        tuned_url = tuned_url.replace("sort=weight%20desc", "")

    return tuned_url


def write_endpoint_to_file(endpoint_requests, endpoint):
    os.makedirs(os.path.dirname(ROOT_DIR + '/generated-data/'), exist_ok=True)
    with open(ROOT_DIR + '/generated-data/' + endpoint + '-real-data.json', 'w') as writer:
        json.dump(endpoint_requests, writer, indent=4)
    print(ROOT_DIR + '/generated-data/' + endpoint + '-real-data.json' + " successfully generated!")


def write_queries_to_file(queries):
    os.makedirs(os.path.dirname(ROOT_DIR + '/generated-data/'), exist_ok=True)
    with open(ROOT_DIR + '/generated-data/queries.json', 'w') as writer:
        json.dump([queries], writer, indent=4)
    print(ROOT_DIR + '/generated-data/queries.json successfully generated!')


def main():
    queries = {}
    for endpoint in ENDPOINTS:
        print("Processing " + endpoint + " requests")

        endpoint_requests = []

        # We perform four iterations to extract more data into de dataset files
        for iteration in range(0, MAX_ITERATIONS):
            old_requests = get_raw_data(endpoint, iteration)
            (requests, qs) = append_samples_to_data_set_files(old_requests)
            endpoint_requests.extend(requests)
            queries = combine_queries(queries, qs)
        write_endpoint_to_file(endpoint_requests, endpoint)

    write_queries_to_file(queries)

    if GENERATION_MODE == "platform":
        collapse_empathize_files()


def combine_queries(queries, qs):
    keys = queries.keys() | qs.keys()
    combined_queries = {key: queries.get(key, []) + qs.get(key, []) for key in keys}
    return combined_queries


def collapse_empathize_files():
    print("Collapsing the empathize and autocomplete files...")
    try:
        autocomplete = []
        empathize = []
        with open(ROOT_DIR + '/generated-data/autocomplete-real-data.json') as fp:
            autocomplete = json.loads(fp.read())

        with open(ROOT_DIR + '/generated-data/empathize-real-data.json') as fp:
            empathize = json.loads(fp.read())

        for e in autocomplete:
            empathize.append(e)

        os.remove(ROOT_DIR + '/generated-data/empathize-real-data.json')
        write_endpoint_to_file(empathize, "empathize")

        os.remove(ROOT_DIR + "/generated-data/autocomplete-real-data.json")

        print("Files successfully collapsed!")
    except FileNotFoundError:
        print("Cannot collapse empathize files")


def load_config():
    global INSTANCES, LANGUAGES, ES_USER, ES_PASSWORD, ES_HOST, GENERATION_MODE, ENDPOINTS, es
    parser = configparser.ConfigParser()

    with open(ROOT_DIR + "/data-generation/options.ini") as stream:
        parser.read_string("[config]\n" + stream.read())

    INSTANCES = parser.get("config", "INSTANCES").split(',')
    LANGUAGES = parser.get("config", "LANGUAGES").split(',')
    ES_HOST = parser.get("config", "ES_HOST")
    ES_USER = parser.get("config", "ES_USER")
    ES_PASSWORD = parser.get("config", "ES_PASSWORD")
    GENERATION_MODE = parser.get("config", "GENERATION_MODE")
    ENDPOINTS = parser.get("config", "ENDPOINTS").split(',')

    if GENERATION_MODE not in ALLOWED_GENERATION_MODES:
        print("[ERROR] GENERATION_MODE must be in [" + ', '.join(ALLOWED_GENERATION_MODES) + "]")
        exit()

    es = Elasticsearch(
        hosts=[ES_HOST],
        http_auth=(ES_USER, ES_PASSWORD),
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    load_config()
    main()
