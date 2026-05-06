def validate_article(article):
    required_fields = ['titre', 'contenu', 'url']
    for field in required_fields:
        if not article.get(field) or len(str(article.get(field))) < 5:
            return False
    return True

# Test simple
if __name__ == "__main__":
    sample = {"titre": "Test", "contenu": "Ceci est un test", "url": "http://test.com"}
    print(f"Qualité OK : {validate_article(sample)}")