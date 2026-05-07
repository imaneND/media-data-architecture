# airflow/dags/dag_streaming.py
# DAG Airflow : Surveillance du streaming Kafka
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'binome-projet',
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
    'email_on_failure': False,
}

with DAG(
    dag_id='pipeline_streaming_articles',
    default_args=default_args,
    description='Surveillance et traitement du streaming Kafka',
    schedule_interval='*/15 * * * *',  # Toutes les 15 minutes
    catchup=False,
    tags=['streaming', 'kafka'],
) as dag:

    # Tâche 1 : Vérifier que Kafka est actif
    def check_kafka():
        from kafka import KafkaConsumer
        try:
            consumer = KafkaConsumer(
                'articles-presse',
                bootstrap_servers='localhost:9092',
                consumer_timeout_ms=5000
            )
            print('✅ Kafka actif et topic disponible')
            consumer.close()
        except Exception as e:
            print(f'⚠️ Kafka non disponible : {e}')

    kafka_check_task = PythonOperator(
        task_id='verifier_kafka',
        python_callable=check_kafka,
    )

    # Tâche 2 : Traitement Silver après streaming
    def task_silver_streaming():
        from datalake.silver_layer import process_bronze_to_silver
        process_bronze_to_silver()

    silver_streaming_task = PythonOperator(
        task_id='traitement_silver_streaming',
        python_callable=task_silver_streaming,
    )

    # Tâche 3 : Mise à jour Gold
    def task_gold_streaming():
        from datalake.gold_layer import process_silver_to_gold
        process_silver_to_gold()

    gold_streaming_task = PythonOperator(
        task_id='mise_a_jour_gold',
        python_callable=task_gold_streaming,
    )

    # Ordre d'exécution
    kafka_check_task >> silver_streaming_task >> gold_streaming_task