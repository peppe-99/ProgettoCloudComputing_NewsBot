import json
import logging
import azure.functions as func
import requests

from config import DefaultConfig


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Arrivata una richiesta HTTP')

    default_config = DefaultConfig()

    MKT = 'it-IT'
    SORT_BY = 'Revelance'
    COUNT = 5

    soggetto_notizia = req.params.get('subject')
    if not soggetto_notizia:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            soggetto_notizia = req_body.get('subject')

    if soggetto_notizia:
        logging.info(f'Soggetto: {soggetto_notizia}')
        
        params = {'q': soggetto_notizia, 'mkt': MKT, 'sortBy': SORT_BY, 'count': COUNT}
        headers = {'Ocp-Apim-Subscription-Key': default_config.BING_KEY}
        try:
            response = requests.get(default_config.SEARCH_URL, headers=headers, params=params)
            response.raise_for_status()

            response = dict(response.json())

            notizie = {}
            for notizia in response["value"]:
                notizie[notizia["name"]] = notizia["url"]
            
            notizie_json = json.dumps(notizie)
            
            return func.HttpResponse(notizie_json, status_code=200)

        except Exception as exception:
            logging.error(exception)
            raise exception

    else:
        logging.info('Nessun soggetto passato')
        return func.HttpResponse(
             "La funzione è stata invocata con successo. Passa un soggetto nella query o nel body della richiesta.",
             status_code=200
        )
