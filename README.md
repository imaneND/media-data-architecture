# 🗞️ Plateforme Big Data — Analyse de Tendances Médiatiques

> Projet réalisé dans le cadre du cours **Architecture de Données**  
> 4ème Année Ingénierie Data — 2025/2026

---

## 📋 Description

Plateforme **Big Data distribuée** capable de collecter automatiquement des articles de presse 
provenant de sources marocaines et internationales, puis de les stocker, transformer et analyser 
afin d'identifier les **tendances médiatiques en temps réel**.

### 🎯 Objectifs
- 📰 Collecter des milliers d'articles automatiquement
- 📊 Identifier les tendances d'actualité
- 🔍 Analyser les thèmes dominants par source
- ⚡ Suivre les événements en temps réel via Kafka
- ✅ Garantir la qualité et la gouvernance des données

---

## 🏗️ Architecture Globale

```
Sites Web → Scraping → Kafka → MinIO Bronze → Silver → Gold → PostgreSQL → Grafana
                                     ↑                              ↑
                                 Data Lake                    Data Warehouse
                              (Médaillon)                   (Analytique)
```

---

## 🛠️ Technologies Utilisées

| Composant | Technologie | Rôle |
|---|---|---|
| Scraping | Python, BeautifulSoup | Collecte des articles |
| Streaming | Apache Kafka | Ingestion temps réel |
| Data Lake | MinIO (S3) | Stockage Bronze/Silver/Gold |
| Orchestration | Apache Airflow | Planification des pipelines |
| Validation | Pydantic | Qualité des données |
| Warehouse | PostgreSQL | Stockage analytique |
| Dashboards | Grafana | Visualisation des tendances |
| Monitoring | Prometheus | Supervision des services |
| Déploiement | Docker | Conteneurisation complète |

---

## 📰 Sources de Données

| Source | Pays | Langue |
|---|---|---|
| Hespress | 🇲🇦 Maroc | Arabe |
| Al Jazeera | 🇶🇦 Qatar | Arabe / Anglais |
| BBC News | 🇬🇧 Royaume-Uni | Anglais |
| The Guardian | 🇬🇧 Royaume-Uni | Anglais |

---

## 🚀 Installation et Démarrage

### Prérequis
- Docker Desktop installé et démarré
- Python 3.10+
- Git

### 1. Cloner le dépôt
```bash
git clone https://github.com/imaneND/media-data-architecture.git
cd media-data-architecture
```

### 2. Installer les dépendances Python
```bash
pip install -r requirements.txt
```

### 3. Démarrer tous les services Docker
```bash
docker compose up -d
```

### 4. Lancer le pipeline complet
```bash
# Collecter les articles
python -m ingestion.batch_collector

# Nettoyer les données (Silver Layer)
python -m datalake.silver_layer

# Analyser les tendances (Gold Layer)
python -m datalake.gold_layer

# Charger dans PostgreSQL
python -m warehouse.load_data

# Contrôles qualité
python -m quality.data_quality
```

---

## 📊 Accès aux Interfaces

| Service | URL | Identifiants |
|---|---|---|
| 🗄️ MinIO | http://localhost:9001 | minioadmin / minioadmin123 |
| 🔄 Airflow | http://localhost:8080 | airflow / airflow |
| 📊 Grafana | http://localhost:3000 | admin / admin |
| 📡 Prometheus | http://localhost:9090 | — |

---

## 📁 Structure du Projet

```
media-data-architecture/
├── 🐳 docker-compose.yml        # Orchestration des services
├── 📦 requirements.txt          # Dépendances Python
├── 📖 README.md
│
├── scraper/                     # Scrapers par source
│   ├── base_scraper.py
│   ├── hespress.py
│   ├── bbc.py
│   ├── aljazeera.py
│   └── the_guardian.py
│
├── ingestion/                   # Ingestion batch + streaming
│   ├── batch_collector.py
│   └── kafka_producer.py
│
├── datalake/                    # Architecture Médaillon
│   ├── minio_client.py          # Connexion MinIO
│   ├── silver_layer.py          # Bronze → Silver
│   └── gold_layer.py            # Silver → Gold
│
├── models/                      # Validation Pydantic
│   ├── article_model.py
│   └── test_pydantic.py
│
├── warehouse/                   # Data Warehouse PostgreSQL
│   ├── create_tables.sql
│   └── load_data.py
│
├── airflow/dags/                # Orchestration Airflow
│   ├── dag_batch.py
│   └── dag_streaming.py
│
├── quality/                     # Qualité des données
│   └── data_quality.py
│
├── monitoring/                  # Monitoring
│   └── prometheus.yml
│
└── visualisation/               # Dashboards Grafana
    └── grafana_dashboard.json
```

---

## 🎁 Bonus Réalisés

| Bonus | Description |
|---|---|
| **Pydantic** | Validation automatique des articles avec score de qualité |
| **Docker** | Déploiement complet en une seule commande |
| **Qualité** | Contrôles : complétude, cohérence, validité, doublons |

---

## 👥 Équipe

| Membre |
|---|
| **Rania Bikikre** |
| **Imane Nadif** |