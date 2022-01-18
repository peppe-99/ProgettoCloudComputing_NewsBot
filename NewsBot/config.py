#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os


class DefaultConfig:
    """ Bot Configuration """
    PORT = 3978
    APP_TYPE = os.environ.get("MicrosoftAppType", "MultiTenant")
    APP_ID = os.environ.get("MicrosoftAppId", "852840b1-fe07-42ae-9be0-adc8cbb8a14c")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "GiuseppeAntonio99.")

    # LUIS Configuration
    LUIS_APP_ID = os.environ.get("LuisAppId", "6560f383-027d-4ec6-9c14-7771a1588401")
    LUIS_API_KEY = os.environ.get("LuisAPIKey", "4e8c9579120e4f7db2baa1dd80c7cfb4")
    LUIS_API_HOST_NAME = os.environ.get("LuisAPIHostName", "https://luis-news-bot.cognitiveservices.azure.com/")

    # Functions URLs
    NEWS_BY_SUBJECT_FUNCTION_URL = os.environ.get("NewsBySubjectFunctionURL", "https://news-bot-functions.azurewebsites.net/api/NewsBySubjectFunction")
    CLICKBAIT_FUNCTION_URL = os.environ.get("ClickbaitFunctionURL", "https://news-bot-functions.azurewebsites.net/api/clickbaitfunction")

    # CosmosDB Configuration
    COSMOS_DB_URL = os.environ.get("CosmosDBURL", "https://cosmos-db-news-bot.documents.azure.com:443/")
    COSMOS_DB_KEY = os.environ.get("CosmosDBKey", "Kls96q9eAvM13SzxaSObVtqQrK2xegVYyULdvmc1ai3YWAjLVIzHJvFx3rJCIhcqviPwBrKtKo8ImgkVqEl06A==")