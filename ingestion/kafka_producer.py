import json
import time
from kafka import KafkaProducer
from scraper.hespress import HespressScraper
from scraper.the_guardian import GuardianScraper
from scraper.aljazeera import AlJazeeraScraper
from scraper.bbc import BBCScraper

def run_streaming():
    print("🚀 Initialisation du Producer Kafka...")
    try:
        producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            retries=5
        )
    except Exception as e:
        print(f"❌ Impossible de se connecter à Kafka : {e}")
        return

    # Configuration des sources et mapping des catégories
    SOURCES_CONFIG = [
        {
            'scraper': HespressScraper(),
            'mapping': {
                'politique': '/politique',
                'societe': '/societe',
                'economie': '/economie',
                'sport': '/sport',
                'culture': '/art-et-culture'
            }
        },
        {'scraper': GuardianScraper(),
            'mapping': {
                'politique': '/world',
                'economie': '/business',
                'technologie': '/technology',
                'sport': '/sport'
            }
        },
        {
            'scraper': AlJazeeraScraper(),
            'mapping': {
                'politique': '/politics',
                'societe': '/news',  # On utilise /news au lieu de /society qui fait 404                'economie': '/economy',
                'sport': '/sport'
            }
        },
        {
            'scraper': BBCScraper(),
            'mapping': {
                'politique': '/news/politics',
                'economie': '/news/business',
                'sport': '/sport',
                'technologie': '/news/technology'
            }
        }
    ]

    while True:
        for source in SOURCES_CONFIG:
            scraper = source['scraper']
            mapping = source['mapping']
            
            print(f"\n--- 🌐 Source : {scraper.base_url} ---")
            
            for theme_global, url_specifique in mapping.items():
                try:
                    links = scraper.get_article_links(url_specifique)
                    
                    for link in links:
                        # 1. Collecte
                        article = scraper.scrape_article(link)
                        
                        if article:
                            # 2. Pré-traitement (Enrichissement)
                            article['categorie'] = theme_global 
                            
                            # --- 3. FILTRE DE QUALITÉ (Architecture Decision) ---
                            titre = article.get('titre', '')
                            contenu = article.get('contenu', '')
                            
                            # Règle : Titre valide ET contenu substantiel (> 50 chars)
                            if titre != "Sans titre" and len(contenu) > 50:
                                # 4. Ingestion dans Kafka
                                producer.send('articles-presse', value=article)
                                print(f"✅ [{theme_global.upper()}] {article['source']} : {titre[:45]}...")
                            else:
                                # Rejet pour éviter de polluer le Data Lake (GIGO)
                                print(f"🗑️  Article rejeté (Qualité insuffisante) : {link[:50]}...")
                
                except Exception as e:
                    print(f"⚠️ Erreur sur le flux {theme_global} : {e}")
                
                time.sleep(1) # Backoff pour éviter d'être banni par les sites
       
       
        print("\n😴 Cycle complet terminé. Prochain passage dans 10 minutes...")
        time.sleep(600)

if __name__ == "__main__":
    run_streaming()