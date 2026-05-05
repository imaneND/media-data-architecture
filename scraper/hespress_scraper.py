# scraper/hespress_scraper.py
# Scraper pour le site Hespress (actualités marocaines)

import requests                    # Pour faire des requêtes HTTP (visiter un site)
from bs4 import BeautifulSoup      # Pour analyser le HTML
import json                        # Pour sauvegarder en format JSON
from datetime import datetime      # Pour la date/heure
import time                        # Pour attendre entre les requêtes

# Configuration — les URLs à scraper
BASE_URL = 'https://hespress.com'
CATEGORIES = ['/politique', '/economie', '/societe', '/sports']

def get_article_links(category_url):
    """Récupère les liens des articles d'une page de catégorie."""
    try:
        # Envoyer une requête GET (comme si vous visitiez la page)
        response = requests.get(BASE_URL + category_url, timeout=10)
        
        # Vérifier que la requête a réussi (200 = OK)
        if response.status_code != 200:
            print(f'Erreur {response.status_code} pour {category_url}')
            return []
        
        # Analyser le HTML avec BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Trouver tous les liens d'articles
        # IMPORTANT : Inspectez le site pour trouver la bonne balise !
        # Clic droit sur un titre → Inspecter → regardez la balise HTML
        article_links = []
        for link in soup.find_all('a', class_='stretched-link'):
            href = link.get('href', '')
            if href and href.startswith('/'):
                article_links.append(BASE_URL + href)
        
        return article_links[:10]  # Limiter à 10 articles pour les tests
    
    except Exception as e:
        print(f'!!!!!!! Erreur lors de la récupération des liens : {e}')
        return []


def scrape_article(url):
    """Scrape un article complet depuis son URL."""
    try:
        # Attendre 1 seconde pour ne pas surcharger le serveur
        time.sleep(1)
        
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extraire le titre
        # Inspectez Hespress pour trouver la bonne classe CSS !
        title_tag = soup.find('h1', class_='post-title')
        title = title_tag.get_text(strip=True) if title_tag else 'Sans titre'
        
        # Extraire l'auteur
        author_tag = soup.find('span', class_='author')
        author = author_tag.get_text(strip=True) if author_tag else 'Inconnu'
        
        # Extraire la date
        date_tag = soup.find('time')
        date = date_tag.get('datetime', '') if date_tag else ''
        
        # Extraire le contenu
        content_tag = soup.find('div', class_='post-content')
        content = content_tag.get_text(strip=True) if content_tag else ''
        
        # Créer le dictionnaire de l'article
        article = {
            'titre': title,
            'auteur': author,
            'date_publication': date,
            'contenu': content,
            'source': 'Hespress',
            'url': url,
            'categorie': 'unknown',      # à améliorer
            'langue': 'ar',              # Hespress = arabe
            'date_collecte': datetime.now().isoformat()
        }
        
        print(f'  >>>>>>> Collecté : {title[:50]}...')
        return article
    
    except Exception as e:
        print(f'  !!!!!!! Erreur pour {url} : {e}')
        return None


def scrape_hespress():
    """Fonction principale : scrape tous les articles Hespress."""
    all_articles = []
    
    for category in CATEGORIES:
        print(f'\n📰 Scraping catégorie : {category}')
        
        # Étape 1 : Récupérer les liens
        links = get_article_links(category)
        print(f'  Trouvé {len(links)} articles')
        
        # Étape 2 : Scraper chaque article
        for link in links:
            article = scrape_article(link)
            if article:  # Si le scraping a réussi
                all_articles.append(article)
    
    print(f'\n >>>>>>> Total articles collectés : {len(all_articles)}')
    return all_articles


# Ce bloc s'exécute seulement si on lance ce fichier directement
if __name__ == '__main__':
    print(' >>>>>>> Démarrage du scraper Hespress...')
    articles = scrape_hespress()
    
    # Sauvegarder en JSON pour tester
    with open('test_hespress.json', 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    
    print(f' >>>>>>> Sauvegardé dans test_hespress.json')
