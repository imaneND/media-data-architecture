# warehouse/load_data.py
# Charger les données Silver dans PostgreSQL
import psycopg2
import json
from datetime import datetime
from datalake.minio_client import get_client, read_json_from_minio, list_objects, BUCKET_SILVER

# Connexion PostgreSQL (doit correspondre à docker-compose.yml)
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'newsdb',
    'user': 'admin',
    'password': 'admin123'
}

def get_db_connection():
    """Créer une connexion PostgreSQL."""
    conn = psycopg2.connect(**DB_CONFIG)
    print('✅ Connexion PostgreSQL établie')
    return conn

def insert_article(cursor, article):
    """Insérer un article dans la base (ou ignorer si déjà présent)."""
    sql = """
        INSERT INTO articles (
            id, titre, auteur, date_publication, categorie,
            contenu, source, url, langue, nombre_mots, date_collecte
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (url) DO NOTHING
    """
    cursor.execute(sql, (
        article.get('id'),
        article.get('titre'),
        article.get('auteur'),
        article.get('date_publication') or None,
        article.get('categorie'),
        article.get('contenu'),
        article.get('source'),
        article.get('url'),
        article.get('langue'),
        article.get('nombre_mots', 0),
        article.get('date_collecte') or None
    ))

def load_silver_to_warehouse():
    """Charger tous les fichiers Silver dans PostgreSQL."""
    minio_client = get_client()
    db_conn = get_db_connection()
    cursor = db_conn.cursor()

    silver_files = list_objects(minio_client, BUCKET_SILVER)
    total_inserted = 0

    for file_name in silver_files:
        articles = read_json_from_minio(minio_client, BUCKET_SILVER, file_name)

        for article in articles:
            insert_article(cursor, article)
            total_inserted += 1

        db_conn.commit()
        print(f'  ✅ {file_name} → {len(articles)} articles chargés')

    cursor.close()
    db_conn.close()
    print(f'\n🏆 Total chargé dans PostgreSQL : {total_inserted} articles')

if __name__ == '__main__':
    load_silver_to_warehouse()