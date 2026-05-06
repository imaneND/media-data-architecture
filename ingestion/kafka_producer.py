import json
from kafka import KafkaProducer
from scraper.hespress_scraper import HespressScraper

def run_producer():
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    scraper = HespressScraper()
    print("🚀 Début du streaming Hespress...")
    
    # On scrape la catégorie politique
    articles = scraper.scrape_category("/politique")
    
    for article in articles:
        producer.send('articles-presse', value=article)
        print(f"✅ Envoyé à Kafka : {article['titre'][:50]}...")
    
    producer.flush()

if __name__ == "__main__":
    run_producer()