# datalake/gold_layer.py
# Transformation Silver → Gold : Agrégations et analyses
from collections import Counter
from datetime import datetime
import re
from datalake.minio_client import get_client, read_json_from_minio, write_json_to_minio
from datalake.minio_client import list_objects, BUCKET_SILVER, BUCKET_GOLD

# Mots vides à ignorer dans l'analyse
STOPWORDS = {'le', 'la', 'les', 'de', 'du', 'des', 'en', 'un', 'une',
             'et', 'est', 'il', 'elle', 'ils', 'que', 'qui', 'à', 'au',
             'the', 'a', 'an', 'in', 'of', 'for', 'on', 'with', 'is', 'are'}

def extract_keywords(text, top_n=10):
    """Extraire les mots les plus fréquents d'un texte."""
    if not text:
        return []
    words = re.findall(r'\b[a-zA-ZÀ-ÿ]{4,}\b', text.lower())
    words = [w for w in words if w not in STOPWORDS]
    counter = Counter(words)
    return counter.most_common(top_n)

def compute_gold_stats(all_articles):
    """Calculer les statistiques agrégées pour la couche Gold."""
    by_source = Counter(a.get('source', 'unknown') for a in all_articles)
    by_langue = Counter(a.get('langue', 'unknown') for a in all_articles)
    by_categorie = Counter(a.get('categorie', 'unknown') for a in all_articles)

    by_day = {}
    for article in all_articles:
        date_str = article.get('date_publication', '')[:10]
        if date_str:
            by_day[date_str] = by_day.get(date_str, 0) + 1

    all_text = ' '.join(a.get('contenu', '') for a in all_articles)
    top_keywords = extract_keywords(all_text, top_n=20)

    return {
        'timestamp': datetime.now().isoformat(),
        'total_articles': len(all_articles),
        'articles_par_source': dict(by_source),
        'articles_par_langue': dict(by_langue),
        'articles_par_categorie': dict(by_categorie),
        'articles_par_jour': by_day,
        'top_mots_cles': [{'mot': w, 'frequence': c} for w, c in top_keywords]
    }

def process_silver_to_gold():
    """Créer la couche Gold depuis Silver."""
    client = get_client()
    silver_files = list_objects(client, BUCKET_SILVER)
    print(f'📂 {len(silver_files)} fichiers Silver')

    all_articles = []
    for file_name in silver_files:
        articles = read_json_from_minio(client, BUCKET_SILVER, file_name)
        all_articles.extend(articles)

    print(f'📊 Total articles Silver : {len(all_articles)}')

    gold_stats = compute_gold_stats(all_articles)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    write_json_to_minio(client, BUCKET_GOLD, f'stats_{timestamp}.json', gold_stats)
    write_json_to_minio(client, BUCKET_GOLD, 'stats_latest.json', gold_stats)

    print('✅ Gold layer créée !')
    return gold_stats

if __name__ == '__main__':
    stats = process_silver_to_gold()
    print(f'Top sources : {stats["articles_par_source"]}')
    print(f'Top mots : {stats["top_mots_cles"][:5]}')