import datetime
import logging
from unicodedata import category
import requests
import smtplib
import azure.functions as func
import azure.cosmos.cosmos_client as cosmos_client
import azure.functions as func

from config import DefaultConfig
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)

    default_config = DefaultConfig()

    # Email param and headers
    MKT = 'it-IT'
    headers = {'Ocp-Apim-Subscription-Key': default_config.BING_KEY}

    # Create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "dailynews"
    msg['From'] = "azure.news.bot@gmail.com"


    # Connect to Email
    bot_email = smtplib.SMTP("smtp.gmail.com", 587)
    bot_email.ehlo()
    bot_email.starttls()
    bot_email.login("azure.news.bot@gmail.com","GiuseppeAntonio99.")


    # Connect to CosmosDB and get all registered users
    _cosmos_client = cosmos_client.CosmosClient(default_config.COSMOS_DB_URL, {'masterKey': default_config.COSMOS_DB_KEY})
    users = _cosmos_client.ReadItems(f"dbs/NewsBotDatabase/colls/UtentiRegistrati/")
   
    for user in users:
        email = user['email']
        preferenze = user['preferenze']
        
        html = """\
        <html>
            <head></head>
            <body>
                <h2> Ciao! Ecco qui le tue notizie giornaliere.</h2>
        """    

        for preferenza in preferenze:
            params = {'mkt': MKT, 'category': preferenza}
            html += f'<h3>{preferenza}</h3>'
            try:
                # Search news
                response = requests.get(default_config.SEARCH_NEWS_URL, headers=headers, params=params)
                response.raise_for_status()

                search_results = dict(response.json())
                articles = search_results["value"]

                # Add 3 news for any category
                for article in articles[:3]:
                    html += f'<p>{article["name"]} - <a href="{article["url"]}">leggi</a></p>'

            except Exception as ex:
                raise ex

        # Complete HTML message and send email
        html += '</body></html>'
        msg.attach(MIMEText(html,"html"))
        bot_email.sendmail("azure.news.bot@gmail.com", email, msg.as_string())    
    
    bot_email.quit()
            
