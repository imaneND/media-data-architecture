# models/test_pydantic.py
from models.article_model import valider_article, valider_liste_articles

print('=== TEST PYDANTIC ===')

# Test 1 : Article valide
article_valide = {
    'titre': 'Économie marocaine en hausse',
    'source': 'Hespress',
    'url': 'https://hespress.com/article/123',
    'contenu': 'Le PIB du Maroc a augmenté de 3.5% ' * 5,
    'auteur': 'Ahmed Benali',
    'categorie': 'economie'
}
article, erreur = valider_article(article_valide)
print(f'Test 1 - Valide : {"✅ OK" if article else "❌ ERREUR"}')
if article:
    print(f'  Nombre mots calculé : {article.nombre_mots}')

# Test 2 : Article avec titre vide
article_mauvais = {
    'titre': '',
    'source': 'BBC News',
    'url': 'https://bbc.com/article',
    'contenu': 'Contenu trop court'
}
article, erreur = valider_article(article_mauvais)
print(f'Test 2 - Titre vide : {"✅ Rejeté" if erreur else "❌ Accepté"}')
if erreur:
    print(f'  Erreur : {erreur[:80]}')

# Test 3 : URL invalide
article_url = {
    'titre': 'Article test',
    'source': 'CNN',
    'url': 'url-invalide-sans-http',
    'contenu': 'Contenu suffisant pour le test ' * 3,
}
article, erreur = valider_article(article_url)
print(f'Test 3 - URL invalide : {"✅ Rejeté" if erreur else "❌ Accepté"}')

print('=== TESTS TERMINÉS ===')