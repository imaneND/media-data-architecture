# datalake/gold_layer.py — VERSION AMÉLIORÉE COMPLÈTE
from collections import Counter
from datetime import datetime
import re
from datalake.minio_client import (get_client, read_json_from_minio,
    write_json_to_minio, list_objects, BUCKET_SILVER, BUCKET_GOLD)

# ── STOPWORDS COMPLETS (anglais + français) ───────────────────────────────────
STOPWORDS = {
    # Anglais — mots outils
    'the','a','an','in','of','for','on','with','is','are','was','were',
    'be','been','have','has','had','do','does','this','that','they',
    'from','or','but','not','what','all','can','will','would','could',
    'should','said','also','their','its','our','his','her','him','she',
    'he','we','you','i','it','at','by','as','if','so','up','out',
    'about','into','than','then','when','where','who','which','how',
    # Anglais — trop génériques
    'news','report','says','according','told','people','year','time',
    'make','take','come','know','think','want','need','going','just',
    'more','some','there','been','after','before','first','last',
    'other','over','new','one','two','three','four','five','would',
    # Français — mots outils
    'le','la','les','de','du','des','en','un','une','et','est','il',
    'elle','ils','que','qui','au','par','sur','dans','avec','pour',
    'pas','plus','se','ce','sont','ont','mais','ou','si','ne','lui',
    'nous','vous','eux','mes','ses','leur','leurs','cette','tout',
    # Mots parasites
    'potato','said','also','year','time','day','days','week','month',
}

def extract_keywords(text: str, top_n: int = 20) -> list:
    """Extraire les mots-clés significatifs (4+ lettres, hors stopwords)."""
    if not text:
        return []
    words = re.findall(r'\b[a-zA-ZÀ-ÿ]{4,}\b', text.lower())
    words = [w for w in words if w not in STOPWORDS]
    counter = Counter(words)
    return [{'mot': w, 'frequence': c} for w, c in counter.most_common(top_n)]


def compute_stats_par_source(articles: list) -> dict:
    """Statistiques détaillées par source : total, moyenne mots, top catégorie."""
    sources = {}
    for a in articles:
        src = a.get('source', 'unknown')
        if src not in sources:
            sources[src] = {'total': 0, 'mots': 0, 'categories': Counter()}
        sources[src]['total'] += 1
        sources[src]['mots'] += a.get('nombre_mots', 0)
        sources[src]['categories'][a.get('categorie', 'unknown')] += 1
    result = {}
    for src, d in sources.items():
        top_cat = d['categories'].most_common(1)[0][0] if d['categories'] else 'unknown'
        result[src] = {
            'total_articles': d['total'],
            'moyenne_mots':   round(d['mots'] / d['total'], 1),
            'top_categorie':  top_cat,
        }
    return result


def compute_tendances_par_jour(articles: list) -> dict:
    """Tendances agrégées par jour : nb articles, sources, catégories, mots."""
    par_jour = {}
    for a in articles:
        date = a.get('date_publication', '')[:10]
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        if date not in par_jour:
            par_jour[date] = {'articles': [], 'sources': Counter(), 'categories': Counter()}
        par_jour[date]['articles'].append(a)
        par_jour[date]['sources'][a.get('source', 'unknown')] += 1
        par_jour[date]['categories'][a.get('categorie', 'unknown')] += 1
    result = {}
    for date, d in sorted(par_jour.items()):
        texte = ' '.join(x.get('contenu', '') for x in d['articles'])
        result[date] = {
            'nombre_articles': len(d['articles']),
            'sources':         dict(d['sources']),
            'categories':      dict(d['categories']),
            'top_mots_cles':   extract_keywords(texte, top_n=10),
        }
    return result


def detect_sujets_emergents(articles: list) -> list:
    """Top mots-clés des articles publiés aujourd'hui."""
    today = datetime.now().strftime('%Y-%m-%d')
    recents = [a for a in articles if a.get('date_publication', '')[:10] == today]
    if not recents:
        recents = articles  # fallback si aucun article du jour
    texte = ' '.join(a.get('contenu', '') for a in recents)
    return extract_keywords(texte, top_n=15)


def process_silver_to_gold() -> dict:
    """Pipeline Silver → Gold : analyses complètes."""
    client = get_client()
    silver_files = list_objects(client, BUCKET_SILVER)
    print(f'📂 {len(silver_files)} fichiers Silver trouvés')

    all_articles = []
    for f in silver_files:
        all_articles.extend(read_json_from_minio(client, BUCKET_SILVER, f))

    print(f'📊 Total articles : {len(all_articles)}')

    # Compteurs de base
    by_source    = Counter(a.get('source', 'unknown')    for a in all_articles)
    by_langue    = Counter(a.get('langue', 'unknown')    for a in all_articles)
    by_categorie = Counter(a.get('categorie', 'unknown') for a in all_articles)
    all_text     = ' '.join(a.get('contenu', '')          for a in all_articles)

    gold_stats = {
        'timestamp':              datetime.now().isoformat(),
        'total_articles':         len(all_articles),
        'articles_par_source':    dict(by_source),
        'articles_par_langue':    dict(by_langue),
        'articles_par_categorie': dict(by_categorie),
        'top_mots_cles':          extract_keywords(all_text, top_n=25),
        'stats_par_source':       compute_stats_par_source(all_articles),
        'tendances_par_jour':     compute_tendances_par_jour(all_articles),
        'sujets_emergents':       detect_sujets_emergents(all_articles),
    }

    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    write_json_to_minio(client, BUCKET_GOLD, f'stats_{ts}.json',  gold_stats)
    write_json_to_minio(client, BUCKET_GOLD, 'stats_latest.json', gold_stats)

    print(f'Top sources    : {dict(list(by_source.items())[:3])}')
    print(f'Top catégories : {dict(list(by_categorie.items())[:3])}')
    print(f'Top mots-clés  : {[m["mot"] for m in gold_stats["top_mots_cles"][:5]]}')
    print(f'Sujets émerg.  : {[m["mot"] for m in gold_stats["sujets_emergents"][:5]]}')
    print('✅ Gold layer créée !')
    return gold_stats


if __name__ == '__main__':
    process_silver_to_gold()