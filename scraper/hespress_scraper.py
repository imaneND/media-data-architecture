from scraper.base_scraper import BaseScraper
from datetime import datetime

class HespressScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.hespress.com"

    def scrape_category(self, category_path):
        url = f"{self.base_url}{category_path}"
        soup = self.get_soup(url)
        articles = []
        
        if soup:
            # Sélecteur à adapter selon le site actuel
            links = [a['href'] for a in soup.select('h3.card-title a')][:5] 
            for link in links:
                detail = self.scrape_article(link)
                if detail: articles.append(detail)
        return articles

    def scrape_article(self, url):
        soup = self.get_soup(url)
        if not soup: return None
        
        return {
            "titre": soup.find('h1').get_text(strip=True) if soup.find('h1') else "Sans titre",
            "contenu": " ".join([p.get_text() for p in soup.select('div.article-content p')]),
            "source": "Hespress",
            "url": url,
            "langue": "ar",
            "date_collecte": datetime.now().isoformat()
        }