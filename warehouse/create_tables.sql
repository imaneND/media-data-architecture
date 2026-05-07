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