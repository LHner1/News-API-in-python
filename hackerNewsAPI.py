# Funktionierende Version
import requests
import pandas as pd
import time
import datetime
from newspaper import Article
import json
import logging

def get_stories():
    #url = 'https://hacker-news.firebaseio.com/v0/topstories.json'
    url = "https://hacker-news.firebaseio.com/v0/newstories.json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f"Failed to get stories. Status code: {response.status_code}")
        return None

def get_news():
    top_stories = get_stories()
    columns = ["Title", "Date", "Text", "Link"]
    
    df = pd.DataFrame(columns=columns)
    current_time = int(time.time())
    
    session = requests.Session()
    
    for story_id in top_stories:
        response = session.get(f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json?print=pretty')
    
        content = json.loads(response.text)
    
        creation_date = content["time"]
        time_difference = current_time - creation_date
    
        # Wenn Artikel älter als 24h
        if time_difference > 86400:
            break
    
        try:
            news_article = Article(url=content["url"], language="en")
            news_article.download()
            news_article.parse()
            news_article.nlp()
        
            title = news_article.title
            date = news_article.publish_date
    
            if not date:
                date = datetime.datetime.fromtimestamp(content["time"])
            text = news_article.text.replace("\n\n", "\n")
    
            df = pd.concat([df, pd.DataFrame({"Title": [content["title"]], "Date": [date], "Text": [text], "Link": [content["url"]]})], ignore_index=True)
    
        except Exception as e:
                        print(f"Error processing article: {e}")

    return df