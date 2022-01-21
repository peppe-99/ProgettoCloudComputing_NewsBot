import os

class DefaultConfig:

    COSMOS_DB_URL = os.environ.get("CosmosDBURL", "")
    COSMOS_DB_KEY = os.environ.get("CosmosDBKey", "")
    BING_KEY = os.environ.get("BingKey", "")
    SEARCH_NEWS_URL = os.environ.get("SearchNewsURL", "")
    SEARCH_URL = os.environ.get("SearchURL", "")
