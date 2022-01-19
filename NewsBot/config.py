#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os


class DefaultConfig:
    """ Bot Configuration """
    PORT = 3978
    APP_TYPE = os.environ.get("MicrosoftAppType", "MultiTenant")
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")

    # LUIS Configuration
    LUIS_APP_ID = os.environ.get("LuisAppId", "")
    LUIS_API_KEY = os.environ.get("LuisAPIKey", "")
    LUIS_API_HOST_NAME = os.environ.get("LuisAPIHostName", "")

    # Functions URLs
    NEWS_BY_SUBJECT_FUNCTION_URL = os.environ.get("NewsBySubjectFunctionURL", "")
    CLICKBAIT_FUNCTION_URL = os.environ.get("ClickbaitFunctionURL", "")

    # CosmosDB Configuration
    COSMOS_DB_URL = os.environ.get("CosmosDBURL", "")
    COSMOS_DB_KEY = os.environ.get("CosmosDBKey", "")