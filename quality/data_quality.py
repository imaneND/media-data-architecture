# quality/data_quality.py — CONTRÔLES QUALITÉ COMPLETS
import json
from datetime import datetime
import psycopg2

DB_CONFIG = {
    'host': 'localhost', 'port': 5432,
    'database': 'newsdb', 'user': 'admin', 'password': 'admin123'
}

def run_quality_checks() -> dict:
    """Exécuter tous les contrôles qualité sur les données PostgreSQL."""
    conn   = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    rapport = {'timestamp': datetime.now().isoformat(), 'tests': {}}

    print('\n🔍 CONTRÔLES QUALITÉ DES DONNÉES')
    print('=' * 45)

    # TEST 1 : Articles sans titre
    cursor.execute("SELECT COUNT(*) FROM articles WHERE titre IS NULL OR titre = ''")
    sans_titre = cursor.fetchone()[0]
    rapport['tests']['sans_titre'] = {
        'valeur': sans_titre, 'statut': '✅ OK' if sans_titre == 0 else '❌ ECHEC'
    }
    print(f'  Articles sans titre      : {sans_titre}  → {rapport["tests"]["sans_titre"]["statut"]}')

    # TEST 2 : Dates manquantes
    cursor.execute("SELECT COUNT(*) FROM articles WHERE date_publication IS NULL")
    sans_date = cursor.fetchone()[0]
    rapport['tests']['sans_date'] = {
        'valeur': sans_date, 'statut': '✅ OK' if sans_date == 0 else '⚠️ AVERTISSEMENT'
    }
    print(f'  Articles sans date       : {sans_date}  → {rapport["tests"]["sans_date"]["statut"]}')

    # TEST 3 : Contenu trop court
    cursor.execute("SELECT COUNT(*) FROM articles WHERE LENGTH(contenu) < 100")
    contenu_court = cursor.fetchone()[0]
    rapport['tests']['contenu_court'] = {
        'valeur': contenu_court, 'statut': '✅ OK' if contenu_court == 0 else '⚠️ AVERTISSEMENT'
    }
    print(f'  Contenu < 100 caractères : {contenu_court}  → {rapport["tests"]["contenu_court"]["statut"]}')

    # TEST 4 : Doublons URL
    cursor.execute("SELECT COUNT(*) FROM (SELECT url FROM articles GROUP BY url HAVING COUNT(*) > 1) t")
    doublons = cursor.fetchone()[0]
    rapport['tests']['doublons'] = {
        'valeur': doublons, 'statut': '✅ OK' if doublons == 0 else '❌ ECHEC'
    }
    print(f'  Doublons URL             : {doublons}  → {rapport["tests"]["doublons"]["statut"]}')

    # TEST 5 : Catégories inconnues
    cursor.execute("SELECT COUNT(*) FROM articles WHERE categorie = 'unknown'")
    cat_unknown = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM articles")
    total = cursor.fetchone()[0]
    pct = round(cat_unknown / total * 100, 1) if total > 0 else 0
    rapport['tests']['categorie_unknown'] = {
        'valeur': cat_unknown, 'pourcentage': pct,
        'statut': '✅ OK' if pct < 20 else '⚠️ AVERTISSEMENT'
    }
    print(f'  Catégories inconnues     : {cat_unknown}/{total} ({pct}%)  → {rapport["tests"]["categorie_unknown"]["statut"]}')

    # SCORE GLOBAL
    nb_ok    = sum(1 for t in rapport['tests'].values() if '✅' in t['statut'])
    nb_tests = len(rapport['tests'])
    score    = round(nb_ok / nb_tests * 100, 1)
    rapport['score_global'] = score
    rapport['total_articles'] = total

    print('=' * 45)
    print(f'  SCORE QUALITÉ : {nb_ok}/{nb_tests} tests OK → {score}%')
    print('=' * 45)

    conn.close()
    return rapport


if __name__ == '__main__':
    rapport = run_quality_checks()
    print(json.dumps(rapport, indent=2, ensure_ascii=False))