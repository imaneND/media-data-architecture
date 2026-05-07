import json
import io
import time
from minio import Minio
from datetime import datetime
from scraper.hespress import HespressScraper
from scraper.the_guardian import GuardianScraper
from scraper.aljazeera import AlJazeeraScraper
from scraper.bbc import BBCScraper

def run_batch():
    print("📦 Démarrage du Batch vers MinIO (Data Lake)...")
    client = Minio("localhost:9000", access_key="minioadmin", secret_key="minioadmin123", secure=False)
    bucket = "bronze"
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)

    # Liste de tous nos scrapers
    scrapers = [HespressScraper(), GuardianScraper(), AlJazeeraScraper(), BBCScraper()]

    for scraper in scrapers:
        source_name = scraper.__class__.__name__.replace('Scraper', '').lower()
        print(f"📥 Collecte pour la source : {source_name}")
        
        # On prend une catégorie par défaut pour le batch (ex: économie)
        # Tu peux aussi boucler sur plusieurs catégories ici
        articles = scraper.get_article_links("/economy" if "bbc" not in source_name else "/news/business")
        
        collected_data = []
        for link in articles:
            detail = scraper.scrape_article(link)
            if detail:
                collected_data.append(detail)
        
        if collected_data:
            data = json.dumps(collected_data, ensure_ascii=False).encode('utf-8')
            filename = f"{source_name}/{datetime.now().strftime('%Y/%m/%d/%H%M')}.json"
            
            client.put_object(bucket, filename, io.BytesIO(data), len(data), content_type='application/json')
            print(f"💾 {len(collected_data)} articles sauvés dans {bucket}/{filename}")
        
        time.sleep(2) # Pause entre les sources

if __name__ == "__main__":
    run_batch()