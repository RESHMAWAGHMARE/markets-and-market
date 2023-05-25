import requests
from bs4 import BeautifulSoup
import spacy
import csv
from datetime import datetime, timedelta

# Function to scrape news articles from a given website
def scrape_news(url):
    # Fetch the website content
    response = requests.get(url)
    content = response.content
    
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(content, 'html.parser')
    
    # Find the news articles
    articles = soup.find_all('article')
    
    # Extract the relevant information from each article
    news_data = []
    for article in articles:
        title = article.find('h3').text.strip()
        summary = article.find('p').text.strip()
        news_data.append({'Title': title, 'Summary': summary})
    
    return news_data

# Function to perform Named Entity Recognition on the news data
def perform_ner(news_data):
    # Load the NER model (Spacy's pre-trained model)
    nlp = spacy.load('en_core_web_sm')
    
    for article in news_data:
        title_entities = []
        summary_entities = []
        
        # Perform NER on the title
        title_doc = nlp(article['Title'])
        for ent in title_doc.ents:
            title_entities.append((ent.text, ent.label_))
        
        # Perform NER on the summary
        summary_doc = nlp(article['Summary'])
        for ent in summary_doc.ents:
            summary_entities.append((ent.text, ent.label_))
        
        article['Title Entities'] = title_entities
        article['Summary Entities'] = summary_entities
    
    return news_data

# Function to tag company names from a list of predefined companies
def tag_companies(news_data, companies):
    for article in news_data:
        tagged_companies = []
        for company in companies:
            if all(word in article['Title'] or word in article['Summary'] for word in company.split()):
                tagged_companies.append(company)
        article['Tagged Companies'] = tagged_companies
    
    return news_data

# Function to save the news data to a CSV file
def save_to_csv(news_data, filename):
    keys = ['Title', 'Summary', 'Title Entities', 'Summary Entities', 'Tagged Companies']
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        writer.writerows(news_data)

# Define the URL of the news website
#url = 'https://www.reuters.com/' 
url = 'https://www.prnewswire.com'

# Scrape the news articles
today = datetime.now().date()
yesterday = today - timedelta(days=1)
news_data = scrape_news(url)

# Filter the news articles for the last two days
filtered_news = [article for article in news_data if today >= article['Date'] >= yesterday]

# Perform NER on the news articles
news_data_with_ner = perform_ner(filtered_news)

# Define a list of predefined companies
companies = ['IBM Systems', 'Google', 'Meta', 'MarketsandMarkets', 'wipro']

# Tag the company names in the news articles
news_data_with_tags = tag_companies(news_data_with_ner, companies)

# Save the news data to a CSV file
filename = 'news_data.csv'
save_to_csv(news_data_with_tags, filename)
