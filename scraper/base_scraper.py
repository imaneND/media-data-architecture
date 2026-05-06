import requests
import time
import random
from bs4 import BeautifulSoup

class BaseScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8',
            'Referer': 'https://www.google.com/'
        }

    def get_soup(self, url):
        try:
            # Pause aléatoire pour ne pas paraître suspect
            time.sleep(random.uniform(1, 2))
            response = requests.get(url, headers=self.headers, timeout=15)
            if response.status_code == 200:
                return BeautifulSoup(response.text, 'html.parser')
            else:
                print(f"⚠️  Erreur {response.status_code} sur {url}")
                return None
        except Exception as e:
            print(f"💥 Erreur de connexion sur {url} : {e}")
            return None