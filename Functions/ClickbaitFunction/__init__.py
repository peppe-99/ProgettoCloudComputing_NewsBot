import logging

import azure.functions as func
import numpy as np
import pandas as pd
from tensorflow.keras import models
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('La funzione è stata invocata')

    title = req.params.get('title')
    if not title:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            title = req_body.get('title')

    if title:
        logging.info(f'Titolo passato: \"{title}\"')
        model = load_model("data_models/model.hdf5")
        headline = (pd.read_csv("data_models/clickbait_data.csv"))['headline'].values

        tokenizer = Tokenizer(num_words=10000)
        tokenizer.fit_on_texts(headline)

        titolo = np.array([title])
        titolo = tokenizer.texts_to_sequences(titolo)
        titolo = pad_sequences(titolo, maxlen=500)

        preds = [round(i[0]) for i in model.predict(titolo)]

        if preds[0] == 1:
            return func.HttpResponse("True", status_code=200)
        else:
            return func.HttpResponse("False", status_code=200)

    else:
        return func.HttpResponse(
             "Inserisci il titolo di un articolo in lingua inglese e ti dirò se è clickbait o meno",
             status_code=200
        )