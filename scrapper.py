import requests
from bs4 import BeautifulSoup
import spacy
import csv
from datetime import datetime, timedelta

def scrape_news(url):
    response = requests.get(url)
    content = response.content
    
    soup = BeautifulSoup(content, 'html.parser')
    
    articles = soup.find_all('article')
    
    news_data = []
    for article in articles:
        title = article.find('h3').text.strip()
        summary = article.find('p').text.strip()
        news_data.append({'Title': title, 'Summary': summary})
    
    return news_data

def perform_ner(news_data):
    nlp = spacy.load('en_core_web_sm')
    
    for article in news_data:
        title_entities = []
        summary_entities = []
        
        title_doc = nlp(article['Title'])
        for ent in title_doc.ents:
            title_entities.append((ent.text, ent.label_))
        
        summary_doc = nlp(article['Summary'])
        for ent in summary_doc.ents:
            summary_entities.append((ent.text, ent.label_))
        
        article['Title Entities'] = title_entities
        article['Summary Entities'] = summary_entities
    
    return news_data

def tag_companies(news_data, companies):
    for article in news_data:
        tagged_companies = []
        for company in companies:
            if all(word in article['Title'] or word in article['Summary'] for word in company.split()):
                tagged_companies.append(company)
        article['Tagged Companies'] = tagged_companies
    
    return news_data

def save_to_csv(news_data, filename):
    keys = ['Title', 'Summary', 'Title Entities', 'Summary Entities', 'Tagged Companies']
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        writer.writerows(news_data)

# Define the URL of the news website
#url = 'https://www.reuters.com/' 
url = 'https://www.prnewswire.com'

today = datetime.now().date()
yesterday = today - timedelta(days=1)
news_data = scrape_news(url)

filtered_news = [article for article in news_data if today >= article['Date'] >= yesterday]

news_data_with_ner = perform_ner(filtered_news)

companies = ['IBM Systems', 'Google', 'Meta', 'MarketsandMarkets', 'wipro']

news_data_with_tags = tag_companies(news_data_with_ner, companies)

filename = 'news_data.csv'
save_to_csv(news_data_with_tags, filename)
