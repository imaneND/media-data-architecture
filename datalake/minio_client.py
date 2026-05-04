# datalake/minio_client.py
# Client MinIO partagé — utilisé par tous les scripts du Data Lake
from minio import Minio
import io
import json

# Paramètres de connexion (doivent correspondre à docker-compose.yml)
MINIO_CONFIG = {
    'endpoint': 'localhost:9000',
    'access_key': 'minioadmin',
    'secret_key': 'minioadmin123',
    'secure': False
}

# Noms des buckets (comme des dossiers dans MinIO)
BUCKET_BRONZE = 'bronze'   # Données brutes
BUCKET_SILVER = 'silver'   # Données nettoyées
BUCKET_GOLD   = 'gold'     # Données analytiques

def get_client():
    """Retourner un client MinIO connecté."""
    return Minio(**MINIO_CONFIG)

def init_buckets():
    """Créer tous les buckets s'ils n'existent pas."""
    client = get_client()
    for bucket in [BUCKET_BRONZE, BUCKET_SILVER, BUCKET_GOLD]:
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)
            print(f'✅ Bucket créé : {bucket}')
        else:
            print(f'ℹ️  Bucket existe déjà : {bucket}')
    return client

def read_json_from_minio(client, bucket, object_name):
    """Lire un fichier JSON depuis MinIO."""
    response = client.get_object(bucket, object_name)
    data = json.loads(response.read().decode('utf-8'))
    response.close()
    return data

def write_json_to_minio(client, bucket, object_name, data):
    """Écrire un objet JSON dans MinIO."""
    encoded = json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8')
    client.put_object(
        bucket, object_name,
        io.BytesIO(encoded), len(encoded),
        content_type='application/json'
    )
    print(f'💾 Sauvegardé : {bucket}/{object_name}')

def list_objects(client, bucket, prefix=''):
    """Lister les fichiers dans un bucket."""
    objects = client.list_objects(bucket, prefix=prefix, recursive=True)
    return [obj.object_name for obj in objects]

if __name__ == '__main__':
    print('🔧 Initialisation des buckets MinIO...')
    client = init_buckets()
    print('✅ MinIO prêt !')
    files = list_objects(client, BUCKET_BRONZE)
    print(f'Fichiers dans bronze : {files[:5]}')