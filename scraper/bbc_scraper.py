# scraper/bbc_scraper.py
# Scraper pour BBC News (actualités internationales en anglais)

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

BASE_URL = 'https://www.bbc.com'
SECTIONS = ['/news/world', '/news/business', '/news/technology']

def scrape_bbc_article(url):
    """Scrape un article BBC."""
    try:
        time.sleep(1)
        headers = {'User-Agent': 'Mozilla/5.0'}  # Simuler un navigateur
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # BBC News — Balises à inspecter sur le site
        title_tag = soup.find('h1', {'data-component': 'headline-block'})
        title = title_tag.get_text(strip=True) if title_tag else 'Sans titre'
        
        # Extraire tous les paragraphes du contenu
        content_blocks = soup.find_all('div', {'data-component': 'text-block'})
        content = ' '.join([b.get_text(strip=True) for b in content_blocks])
        
        return {
            'titre': title,
            'auteur': 'BBC News',
            'date_publication': datetime.now().isoformat(),
            'contenu': content,
            'source': 'BBC News',
            'url': url,
            'categorie': 'unknown',
            'langue': 'en',
            'date_collecte': datetime.now().isoformat()
        }
    except Exception as e:
        print(f'Erreur BBC : {e}')
        return None

if __name__ == '__main__':
    # Test rapide avec un article
    article = scrape_bbc_article('https://www.bbc.com/news/world')
    if article:
        print(f'Titre : {article["titre"]}')
