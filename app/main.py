import json
import os
import sys
from alert import AlertFetcher, AlertUploader
from deduplicate import Deduplicator
from logger import ErrorLogger
from dotenv import load_dotenv


def main():
    if sys.argv[1:]:
        load_dotenv(sys.argv[1])
    TAG = str(os.environ.get("TAG"))
    INPUT_ELASTICSEARCH = str(os.environ.get("INPUT_ELASTICSEARCH"))
    INPUT_INDEX = str(os.environ.get("INPUT_INDEX"))
    INPUT_API_KEY = str(os.environ.get("INPUT_API_KEY"))
    QUERY = str(os.environ.get("QUERY"))
    OUTPUT_ELASTICSEARCH = str(os.environ.get("OUTPUT_ELASTICSEARCH"))
    OUTPUT_INDEX = str(os.environ.get("OUTPUT_INDEX"))
    OUTPUT_API_KEY = str(os.environ.get("OUTPUT_API_KEY"))
    ERROR_LOGFILE = str(os.environ.get("ERROR_LOGFILE"))
    DEDUP_FILE = str(os.environ.get("DEDUP_FILE"))

    error_logger = ErrorLogger(ERROR_LOGFILE, 4096, 5)

    try:
        fetcher = AlertFetcher(
            INPUT_ELASTICSEARCH, verify_certs=False, api_key=INPUT_API_KEY
        )
        uploader = AlertUploader(
            OUTPUT_ELASTICSEARCH, verify_certs=False, api_key=OUTPUT_API_KEY
        )
        deduplicator = Deduplicator(filename=DEDUP_FILE)

        docs = fetcher.fetch(INPUT_INDEX, json.load(open(QUERY)))
        alerts = [doc["_source"] for doc in docs]
        alerts = deduplicator.uniques(alerts)
        enriched_alerts = [{**alert, "tag": TAG} for alert in alerts]
        uploader.upload(OUTPUT_INDEX, enriched_alerts)
        deduplicator.store(alerts)

    except Exception as e:
        error_logger.log(str(e))


if __name__ == "__main__":
    main()
