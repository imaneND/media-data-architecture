import requests
import time
import random
from bs4 import BeautifulSoup

class BaseScraper:
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
        ]

    def get_soup(self, url):
        """Récupère le contenu HTML d'une page avec gestion des erreurs."""
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8'
        }
        try:
            time.sleep(random.uniform(1, 2)) # Pause pour éviter d'être banni
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return BeautifulSoup(response.text, 'html.parser')
            else:
                print(f"!!!!!!! Erreur {response.status_code} pour {url}")
                return None
        except Exception as e:
            print(f"!!!!!!! Erreur de connexion : {e}")
            return None