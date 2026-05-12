# datalake/silver_layer.py
# Transformation Bronze → Silver : Nettoyage et normalisation
import re
from bs4 import BeautifulSoup
from langdetect import detect
import hashlib
from datetime import datetime
from datalake.minio_client import get_client, read_json_from_minio, write_json_to_minio
from datalake.minio_client import list_objects, BUCKET_BRONZE, BUCKET_SILVER
from models.article_model import valider_liste_articles

# ── AJOUT 1 : Mapping URL → Catégorie ────────────────────────────────────────
CATEGORY_MAPPING = {
    'sport':         ['sport', 'football', 'tennis', 'basketball', 'rugby'],
    'politique':     ['politics', 'world', 'government', 'election', 'policy'],
    'economie':      ['business', 'economy', 'finance', 'market', 'trade'],
    'technologie':   ['tech', 'technology', 'science', 'ai', 'digital', 'cyber'],
    'culture':       ['culture', 'arts', 'entertainment', 'music', 'film'],
    'sante':         ['health', 'medical', 'covid', 'virus', 'hospital'],
    'environnement': ['climate', 'environment', 'green', 'energy', 'ecology'],
    'education':     ['education', 'school', 'university', 'student'],
}

def extract_categorie_from_url(url: str, titre: str = '') -> str:
    """Extraire la catégorie depuis l'URL et le titre."""
    text = (url + ' ' + titre).lower()
    for categorie, keywords in CATEGORY_MAPPING.items():
        if any(kw in text for kw in keywords):
            return categorie
    return 'general'

# ── AJOUT 2 : Correction des dates ───────────────────────────────────────────
def fix_date_publication(date_str: str) -> str:
    """Normaliser la date — si absente, utiliser aujourd'hui."""
    if not date_str or not date_str.strip():
        return datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    formats = [
        '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y'
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str.strip()[:19], fmt)
            return dt.strftime('%Y-%m-%dT%H:%M:%S')
        except ValueError:
            continue
    return datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

# ── Fonctions existantes ──────────────────────────────────────────────────────
def clean_html(text):
    """Supprimer les balises HTML d'un texte."""
    if not text:
        return ''
    soup = BeautifulSoup(text, 'html.parser')
    return soup.get_text(separator=' ', strip=True)

def normalize_text(text):
    """Normaliser un texte."""
    if not text:
        return ''
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[\x00-\x1F\x7F]', '', text)
    return text.strip()

def detect_language(text):
    """Détecter la langue d'un texte."""
    try:
        if len(text) < 20:
            return 'unknown'
        return detect(text)
    except:
        return 'unknown'

def generate_id(article):
    """Générer un ID unique basé sur l'URL."""
    url = article.get('url', '')
    return hashlib.md5(url.encode()).hexdigest()[:16]

def clean_article(article):
    """Nettoyer et normaliser un article brut (Bronze → Silver)."""
    raw_content = article.get('contenu', '')
    clean_content = clean_html(raw_content)
    clean_content = normalize_text(clean_content)
    clean_title = normalize_text(clean_html(article.get('titre', '')))
    langue = article.get('langue') or detect_language(clean_content)
    word_count = len(clean_content.split()) if clean_content else 0
    url = article.get('url', '')

    # ── NOUVELLES LIGNES ──────────────────────────────────────────────────────
    # Extraire catégorie automatiquement depuis URL + titre
    categorie = article.get('categorie', 'unknown')
    if not categorie or categorie == 'unknown':
        categorie = extract_categorie_from_url(url, clean_title)

    # Corriger la date de publication
    date_pub = fix_date_publication(article.get('date_publication', ''))
    # ──────────────────────────────────────────────────────────────────────────

    return {
        'id':                     generate_id(article),
        'titre':                  clean_title,
        'auteur':                 normalize_text(article.get('auteur', 'Inconnu')),
        'date_publication':       date_pub,      # ← date corrigée
        'categorie':              categorie,     # ← catégorie extraite
        'contenu':                clean_content,
        'source':                 article.get('source', ''),
        'url':                    url,
        'langue':                 langue,
        'nombre_mots':            word_count,
        'date_collecte':          article.get('date_collecte', ''),
        'date_traitement_silver': datetime.now().isoformat()
    }

def process_bronze_to_silver():
    """Lire tous les fichiers Bronze et créer les fichiers Silver."""
    client = get_client()
    bronze_files = list_objects(client, BUCKET_BRONZE)
    print(f'📂 {len(bronze_files)} fichiers Bronze à traiter')

    seen_ids = set()
    total_processed = 0

    for file_name in bronze_files:
        print(f'\n⚙️  Traitement : {file_name}')
        articles_bruts = read_json_from_minio(client, BUCKET_BRONZE, file_name)

        articles_clean = []
        for article in articles_bruts:
            cleaned = clean_article(article)
            if cleaned['id'] in seen_ids:
                print(f'  ⚠️  Doublon ignoré : {cleaned["url"][:50]}')
                continue
            seen_ids.add(cleaned['id'])
            articles_clean.append(cleaned)

        # Validation Pydantic
        print(f'  🔍 Validation Pydantic de {len(articles_clean)} articles...')
        articles_valides, rapport = valider_liste_articles(articles_clean)
        print(f'  ✅ Valides   : {rapport["valides"]}/{rapport["total"]}')
        print(f'  ❌ Invalides : {rapport["invalides"]}/{rapport["total"]}')
        print(f'  📊 Taux      : {rapport["taux_validite"]}%')

        silver_name = file_name.replace('/', '/silver_', 1) if '/' in file_name else f'silver_{file_name}'
        write_json_to_minio(client, BUCKET_SILVER, silver_name, articles_valides)
        total_processed += len(articles_valides)

    print(f'\n✅ Silver layer prête : {total_processed} articles traités')

if __name__ == '__main__':
    process_bronze_to_silver()