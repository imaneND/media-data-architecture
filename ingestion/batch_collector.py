import json
import io
from minio import Minio
from datetime import datetime
from scraper.hespress_scraper import HespressScraper

def run_batch():
    client = Minio("localhost:9000", access_key="minioadmin", secret_key="minioadmin123", secure=False)
    bucket = "bronze"
    if not client.bucket_exists(bucket): client.make_bucket(bucket)

    scraper = HespressScraper()
    articles = scraper.scrape_category("/societe")
    
    if articles:
        data = json.dumps(articles).encode('utf-8')
        filename = f"hespress/{datetime.now().strftime('%Y-%m-%d_%H%M')}.json"
        client.put_object(bucket, filename, io.BytesIO(data), len(data))
        print(f"💾 Sauvegardé dans MinIO : {filename}")

if __name__ == "__main__":
    run_batch()