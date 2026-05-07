from scraper.base_scraper import BaseScraper
from datetime import datetime

class BBCScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.bbc.com"

    def get_article_links(self, category_path):
        print(f"🔍 Recherche BBC : {category_path}")
        soup = self.get_soup(f"{self.base_url}{category_path}")
        links = []
        if soup:
            # Cherche tous les liens qui contiennent '/news/' ou '/articles/'
            for a in soup.find_all('a', href=True):
                href = a['href']
                if "/news/" in href or "/articles/" in href:
                    full_url = href if href.startswith("http") else f"{self.base_url}{href}"
                    links.append(full_url)
        return list(set(links))[:5]

    def scrape_article(self, url):
        soup = self.get_soup(url)
        if not soup: return None
        
        # BBC utilise souvent h1 pour le titre et 'article' pour le corps
        title = soup.find('h1')
        content = soup.find('article')
        
        return {
            "titre": title.get_text(strip=True) if title else "Sans titre",
            "contenu": content.get_text(strip=True)[:500] if content else "Contenu vide",
            "source": "BBC News",
            "url": url,
            "date_collecte": datetime.now().isoformat()
        }