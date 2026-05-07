from scraper.base_scraper import BaseScraper
from datetime import datetime

class HespressScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.hespress.com"

    def get_article_links(self, category_path):
        print(f"🔍 Recherche de liens dans : {category_path}")
        soup = self.get_soup(f"{self.base_url}{category_path}")
        links = []
        if soup:
            # Sur Hespress, les liens sont souvent dans des h3 avec la classe card-title
            for a in soup.select("h3.card-title a, a.stretched-link"):
                href = a.get('href')
                if href and href.startswith("https"):
                    links.append(href)
        return list(set(links))[:5] # On prend 5 articles pour tester

    def scrape_article(self, url):
        soup = self.get_soup(url)
        if not soup: return None
        
        print(f"📖 Lecture de l'article : {url[:50]}...")
        title = soup.find('h1')
        content = soup.select_one('.article-content, .post-content')
        
        return {
            "titre": title.get_text(strip=True) if title else "Sans titre",
            "contenu": content.get_text(strip=True)[:500] if content else "Contenu vide",
            "source": "Hespress",
            "url": url,
            "date_collecte": datetime.now().isoformat()
        }