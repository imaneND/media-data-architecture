from scraper.base_scraper import BaseScraper
from datetime import datetime

class GuardianScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.theguardian.com"

    def get_article_links(self, category_path):
        print(f"🔍 Recherche The Guardian : {category_path}")
        soup = self.get_soup(f"{self.base_url}{category_path}")
        links = []
        if soup:
            # On cherche les liens dans les titres d'articles (souvent des h3)
            # Les liens The Guardian contiennent souvent l'année (ex: /2024/may/...)
            for a in soup.find_all('a', href=True):
                href = a['href']
                if any(year in href for year in ['/2024/', '/2025/', '/2026/']):
                    full_url = href if href.startswith("http") else f"{self.base_url}{href}"
                    links.append(full_url)
        return list(set(links))[:5]

    def scrape_article(self, url):
        soup = self.get_soup(url)
        if not soup: return None
        
        # Titre : Balise h1
        title = soup.find('h1')
        # Contenu : Souvent dans des div d'article ou paragraphes
        content_div = soup.find('div', {'class': 'article-body-commercial-selector'}) or soup.find('article')
        paragraphs = content_div.find_all('p') if content_div else soup.find_all('p')
        content = " ".join([p.get_text(strip=True) for p in paragraphs[:8]])
        
        return {
            "titre": title.get_text(strip=True) if title else "Sans titre",
            "contenu": content if len(content) > 50 else "Contenu trop court",
            "source": "The Guardian",
            "url": url,
            "langue": "en",
            "date_collecte": datetime.now().isoformat()
        }