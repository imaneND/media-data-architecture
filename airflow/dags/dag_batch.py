# airflow/dags/dag_batch.py
# DAG Airflow : Pipeline batch complet
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
sys.path.insert(0, '/opt/airflow')

# Arguments par défaut du DAG
default_args = {
    'owner': 'binome-projet',
    'start_date': datetime(2024, 1, 1),
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': False,
}

# Définition du DAG
with DAG(
    dag_id='pipeline_batch_articles',
    default_args=default_args,
    description='Pipeline batch : collecte et traitement articles de presse',
    schedule_interval='0 * * * *',  # Toutes les heures
    catchup=False,
    tags=['batch', 'scraping', 'medallion'],
) as dag:

    # Tâche 1 : Scraping et ingestion Bronze
    def task_scraping():
        from ingestion.batch_ingestion import run_batch
        run_batch()

    scraping_task = PythonOperator(
        task_id='scraping_et_ingestion_bronze',
        python_callable=task_scraping,
    )

    # Tâche 2 : Traitement Silver
    def task_silver():
        from datalake.silver_layer import process_bronze_to_silver
        process_bronze_to_silver()

    silver_task = PythonOperator(
        task_id='traitement_silver',
        python_callable=task_silver,
    )

    # Tâche 3 : Traitement Gold
    def task_gold():
        from datalake.gold_layer import process_silver_to_gold
        process_silver_to_gold()

    gold_task = PythonOperator(
        task_id='traitement_gold',
        python_callable=task_gold,
    )

    # Tâche 4 : Chargement Data Warehouse
    def task_warehouse():
        from warehouse.load_data import load_silver_to_warehouse
        load_silver_to_warehouse()

    warehouse_task = PythonOperator(
        task_id='chargement_warehouse',
        python_callable=task_warehouse,
    )

    # Tâche 5 : Contrôle qualité
    def task_quality():
        import psycopg2
        conn = psycopg2.connect(
            host='postgres',
            database='newsdb',
            user='admin',
            password='admin123'
        )
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM articles')
        count = cursor.fetchone()[0]
        conn.close()
        print(f'✅ Articles dans le warehouse : {count}')

    quality_task = PythonOperator(
        task_id='controle_qualite',
        python_callable=task_quality,
    )

    # Ordre d'exécution
    scraping_task >> silver_task >> gold_task >> warehouse_task >> quality_task