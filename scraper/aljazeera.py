from scraper.base_scraper import BaseScraper
from datetime import datetime

class AlJazeeraScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.aljazeera.net"

    def get_article_links(self, category_path):
        print(f"🔍 Recherche Al Jazeera : {category_path}")
        soup = self.get_soup(f"{self.base_url}{category_path}")
        links = []
        if soup:
        # On cherche tous les liens <a> qui contiennent un chiffre (souvent l'ID de l'article)
        # ou qui sont dans la partie principale du site
            for a in soup.find_all('a', href=True):
                href = a['href']
            # Filtre : liens longs, internes, et qui ne sont pas des tags/recherche
                if len(href) > 30 and not any(x in href for x in ['/tags/', '/search/', '/author/']):
                    if href.startswith('/'):
                        links.append(f"{self.base_url}{href}")
                    elif self.base_url in href:
                        links.append(href)
                    
        return list(set(links))[:5]

    def scrape_article(self, url):
        soup = self.get_soup(url)
        if not soup: return None
        
        title = soup.find('h1')
        # Le contenu est souvent dans une div avec cette classe
        content = soup.select_one('.wysiwyg--all-content')
        
        return {
            "titre": title.get_text(strip=True) if title else "Sans titre",
            "contenu": content.get_text(strip=True)[:500] if content else "Contenu vide",
            "source": "Al Jazeera",
            "url": url,
            "date_collecte": datetime.now().isoformat()
        }