# warehouse/load_data.py — VERSION FINALE CORRIGÉE
import psycopg2
import hashlib
from datalake.minio_client import (get_client, read_json_from_minio,
    list_objects, BUCKET_SILVER, BUCKET_GOLD)

DB_CONFIG = {
    'host': 'localhost', 'port': 5432,
    'database': 'newsdb', 'user': 'admin', 'password': 'admin123'
}

def get_db_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    print('✅ Connexion PostgreSQL établie')
    return conn


def insert_article(cursor, article):
    """Insérer un article dans PostgreSQL."""
    article_url = article.get('url') or ''
    if len(article_url) < 10:
        return False

    # Générer l'id depuis l'URL si absent
    article_id = article.get('id') or hashlib.md5(article_url.encode()).hexdigest()[:16]

    try:
        cursor.execute("""
            INSERT INTO articles (
                id, titre, auteur, date_publication, categorie,
                contenu, source, url, langue, nombre_mots, date_collecte
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (url) DO UPDATE SET
                categorie        = EXCLUDED.categorie,
                date_publication = EXCLUDED.date_publication,
                nombre_mots      = EXCLUDED.nombre_mots
        """, (
            article_id,
            article.get('titre', ''),
            article.get('auteur', 'Inconnu'),
            article.get('date_publication') or None,
            article.get('categorie', 'general'),
            article.get('contenu', ''),
            article.get('source', ''),
            article_url,
            article.get('langue', 'unknown'),
            article.get('nombre_mots', 0),
            article.get('date_collecte') or None
        ))
        return True
    except Exception as e:
        print(f'  ⚠️  Erreur insertion : {e}')
        return False


def load_mots_cles(cursor, mots_cles_list: list, source: str = None):
    """Insérer les mots-clés."""
    for item in mots_cles_list:
        cursor.execute("""
            INSERT INTO mots_cles (mot, frequence, source, date_analyse)
            VALUES (%s, %s, %s, CURRENT_DATE)
        """, (item['mot'], item['frequence'], source))


def load_tendances(cursor, tendances_par_jour: dict):
    """Insérer les tendances par jour."""
    for date_str, data in tendances_par_jour.items():
        for source, count in data.get('sources', {}).items():
            for cat in data.get('categories', {}).keys():
                cursor.execute("""
                    INSERT INTO tendances_jour
                    (date_jour, source, categorie, nombre_articles)
                    VALUES (%s, %s, %s, %s)
                """, (date_str, source, cat, count))


def load_silver_to_warehouse():
    """Pipeline complet de chargement Silver → PostgreSQL."""
    minio_client = get_client()
    db_conn      = get_db_connection()
    cursor       = db_conn.cursor()
    total        = 0

    # ── NETTOYAGE AUTOMATIQUE ─────────────────────────────────────────────
    print('\n🗑️  Nettoyage des tables...')
    cursor.execute("TRUNCATE TABLE mots_cles;")
    cursor.execute("TRUNCATE TABLE tendances_jour;")
    cursor.execute("DELETE FROM articles;")
    db_conn.commit()
    print('✅ Tables nettoyées')

    # ── 1. Charger les articles Silver ────────────────────────────────────
    print('\n📰 Chargement des articles Silver...')
    for file_name in list_objects(minio_client, BUCKET_SILVER):
        articles = read_json_from_minio(minio_client, BUCKET_SILVER, file_name)
        valides = 0
        for art in articles:
            if insert_article(cursor, art):
                total += 1
                valides += 1
        db_conn.commit()
        if valides > 0:
            print(f'  ✅ {file_name} → {valides} articles')

    # ── 2. Charger mots-clés et tendances depuis Gold ─────────────────────
    print('\n🔑 Chargement des mots-clés et tendances...')
    try:
        gold = read_json_from_minio(minio_client, BUCKET_GOLD, 'stats_latest.json')
        load_mots_cles(cursor, gold.get('top_mots_cles', []))
        load_mots_cles(cursor, gold.get('sujets_emergents', []), 'emergents')
        load_tendances(cursor, gold.get('tendances_par_jour', {}))
        db_conn.commit()
        print(f'  ✅ {len(gold.get("top_mots_cles", []))} mots-clés chargés')
        print(f'  ✅ {len(gold.get("tendances_par_jour", {}))} jours de tendances')
    except Exception as e:
        print(f'  ⚠️  Gold non disponible : {e}')

    cursor.close()
    db_conn.close()
    print(f'\n🏆 Total chargé : {total} articles dans PostgreSQL')
    print('📊 Grafana se met à jour automatiquement dans 5 minutes !')


if __name__ == '__main__':
    load_silver_to_warehouse()