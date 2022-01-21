import os

class DefaultConfig:

    COSMOS_DB_URL = os.environ.get("CosmosDBURL", "https://cosmos-db-news-bot.documents.azure.com:443/")
    COSMOS_DB_KEY = os.environ.get("CosmosDBKey", "Kls96q9eAvM13SzxaSObVtqQrK2xegVYyULdvmc1ai3YWAjLVIzHJvFx3rJCIhcqviPwBrKtKo8ImgkVqEl06A==")
    BING_KEY = os.environ.get("BingKey", "66c387861a144d088af9b5b6ccb5c613")
    SEARCH_NEWS_URL = os.environ("SearchNewsURL", "https://api.bing.microsoft.com/v7.0/news/")
    SEARCH_URL = os.environ("SearchURL", "https://api.bing.microsoft.com/v7.0/news/search")
