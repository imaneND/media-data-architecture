#  Plateforme Big Data — Analyse de Tendances Médiatiques

##  Description
Plateforme Big Data distribuée pour la collecte, le stockage, 
la transformation et l'analyse automatique d'articles de presse 
provenant de sources marocaines et internationales.

##  Architecture
Scraping → Kafka → MinIO (Bronze) → Silver → Gold → PostgreSQL → Grafana

##  Technologies utilisées

| Composant | Technologie |
|---|---|
| Scraping | Python, BeautifulSoup |
| Streaming | Apache Kafka |
| Data Lake | MinIO |
| Orchestration | Apache Airflow |
| Warehouse | PostgreSQL |
| Dashboards | Grafana |
| Monitoring | Prometheus |
| Validation | Pydantic |
| Déploiement | Docker |

## 🚀 Installation et démarrage

### Prérequis
- Docker Desktop installé
- Python 3.10+
- Git

### Lancer le projet

# 1. Cloner le dépôt
git clone https://github.com/imaneND/media-data-architecture.git
cd media-data-architecture

# 2. Installer les dépendances Python
pip install -r requirements.txt

# 3. Démarrer tous les services
docker compose up -d

##  Accès aux interfaces

| Service | URL | Login |
|---|---|---|
| MinIO | http://localhost:9001 | minioadmin / minioadmin123 |
| Airflow | http://localhost:8080 | airflow / airflow |
| Grafana | http://localhost:3000 | admin / admin |
| Prometheus | http://localhost:9090 | — |

## 📁 Structure du projet

media-data-architecture/
├── docker-compose.yml
├── requirements.txt
├── README.md
├── scraper/
├── ingestion/
├── datalake/
│   ├── minio_client.py
│   ├── bronze_layer.py
│   ├── silver_layer.py
│   └── gold_layer.py
├── models/
│   ├── article_model.py
│   └── test_pydantic.py
├── warehouse/
│   ├── create_tables.sql
│   └── load_data.py
├── airflow/
│   └── dags/
│       ├── dag_batch.py
│       └── dag_streaming.py
├── monitoring/
│   └── prometheus.yml
└── visualisation/
    └── grafana_dashboard.json

## 🎁 Bonus
- **Pydantic** : Validation automatique des articles (titre, URL, contenu, source)
- **Docker** : Déploiement complet en une commande

