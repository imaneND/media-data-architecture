-- warehouse/create_tables.sql
-- Script SQL de création des tables analytiques

-- Table des articles (données complètes)
CREATE TABLE IF NOT EXISTS articles (
    id              VARCHAR(16) PRIMARY KEY,
    titre           TEXT NOT NULL,
    auteur          VARCHAR(255),
    date_publication TIMESTAMP,
    categorie       VARCHAR(100),
    contenu         TEXT,
    source          VARCHAR(100) NOT NULL,
    url             TEXT UNIQUE NOT NULL,
    langue          VARCHAR(10),
    nombre_mots     INTEGER,
    date_collecte   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Vue : Articles par jour
CREATE OR REPLACE VIEW articles_par_jour AS
SELECT
    DATE(date_publication) AS jour,
    source,
    COUNT(*) AS nombre_articles,
    AVG(nombre_mots) AS moyenne_mots
FROM articles
WHERE date_publication IS NOT NULL
GROUP BY DATE(date_publication), source
ORDER BY jour DESC;

-- Vue : Articles par thème
CREATE OR REPLACE VIEW articles_par_theme AS
SELECT
    categorie,
    source,
    COUNT(*) AS nombre_articles
FROM articles
WHERE categorie != 'unknown'
GROUP BY categorie, source
ORDER BY nombre_articles DESC;

-- Vue : Top sources
CREATE OR REPLACE VIEW top_sources AS
SELECT
    source,
    COUNT(*) AS total_articles,
    MIN(date_publication) AS premier_article,
    MAX(date_publication) AS dernier_article
FROM articles
GROUP BY source
ORDER BY total_articles DESC;

COMMENT ON TABLE articles IS 'Articles de presse collectés - couche Silver';

-- Vue : Articles par pays
CREATE OR REPLACE VIEW articles_par_pays AS
SELECT
    CASE source
        WHEN 'Hespress' THEN 'Maroc'
        WHEN 'Akhbarona' THEN 'Maroc'
        WHEN 'BBC News' THEN 'Royaume-Uni'
        WHEN 'Al Jazeera' THEN 'Qatar'
        WHEN 'Reuters' THEN 'Royaume-Uni'
        WHEN 'CNN' THEN 'USA'
        ELSE 'Inconnu'
    END AS pays,
    COUNT(*) AS nombre_articles
FROM articles
GROUP BY pays
ORDER BY nombre_articles DESC;

-- ── NOUVELLES TABLES À AJOUTER ────────────────────────────────────────────

-- Table des mots-clés extraits par la Gold Layer
CREATE TABLE IF NOT EXISTS mots_cles (
    id            SERIAL PRIMARY KEY,
    mot           VARCHAR(150) NOT NULL,
    frequence     INTEGER      NOT NULL,
    source        VARCHAR(100),
    date_analyse  DATE         DEFAULT CURRENT_DATE,
    created_at    TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

-- Table des tendances agrégées par jour et par source
CREATE TABLE IF NOT EXISTS tendances_jour (
    id              SERIAL PRIMARY KEY,
    date_jour       DATE         NOT NULL,
    source          VARCHAR(100),
    categorie       VARCHAR(100),
    nombre_articles INTEGER      DEFAULT 0,
    created_at      TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

-- ── INDEX POUR ACCÉLÉRER LES REQUÊTES GRAFANA ─────────────────────────────
CREATE INDEX IF NOT EXISTS idx_articles_date
    ON articles(date_publication);
CREATE INDEX IF NOT EXISTS idx_articles_source
    ON articles(source);
CREATE INDEX IF NOT EXISTS idx_articles_categorie
    ON articles(categorie);
CREATE INDEX IF NOT EXISTS idx_mots_cles_date
    ON mots_cles(date_analyse);
CREATE INDEX IF NOT EXISTS idx_mots_cles_mot
    ON mots_cles(mot);

-- ── VUES ANALYTIQUES ──────────────────────────────────────────────────────
CREATE OR REPLACE VIEW mots_cles_top AS
SELECT mot, SUM(frequence) AS total
FROM mots_cles
GROUP BY mot
ORDER BY total DESC
LIMIT 20;

CREATE OR REPLACE VIEW evolution_quotidienne AS
SELECT
    DATE(date_publication) AS jour,
    source,
    categorie,
    COUNT(*)               AS nombre_articles,
    AVG(nombre_mots)       AS moyenne_mots
FROM articles
WHERE date_publication IS NOT NULL
GROUP BY DATE(date_publication), source, categorie
ORDER BY jour DESC;