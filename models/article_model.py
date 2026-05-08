# models/article_model.py
# Modèle Pydantic pour valider les articles de presse

from pydantic import BaseModel, field_validator, model_validator
from typing import Optional


class ArticleModel(BaseModel):
    """Modèle de validation d'un article de presse."""

    # Champs obligatoires
    titre: str
    source: str
    url: str
    contenu: str

    # Champs optionnels
    auteur: Optional[str] = 'Inconnu'
    date_publication: Optional[str] = None
    categorie: Optional[str] = 'unknown'
    langue: Optional[str] = None
    nombre_mots: Optional[int] = 0
    date_collecte: Optional[str] = None

    @field_validator('titre')
    @classmethod
    def titre_non_vide(cls, v):
        """Le titre ne doit pas être vide."""
        v = v.strip()
        if len(v) < 3:
            raise ValueError('Titre trop court (minimum 3 caractères)')
        return v

    @field_validator('contenu')
    @classmethod
    def contenu_suffisant(cls, v):
        """Le contenu doit avoir au moins 50 caractères."""
        if len(v.strip()) < 50:
            raise ValueError('Contenu trop court (minimum 50 caractères)')
        return v.strip()

    @field_validator('url')
    @classmethod
    def url_valide(cls, v):
        """L'URL doit commencer par http."""
        if not v.startswith('http'):
            raise ValueError(f'URL invalide : {v}')
        return v

    @field_validator('source')
    @classmethod
    def source_connue(cls, v):
        """La source doit être une valeur connue."""
        sources_valides = [
            'Hespress', 'BBC News', 'Al Jazeera',
            'The Guardian', 'Reuters', 'CNN'
        ]
        if v not in sources_valides:
            print(f'  ⚠️  Source inconnue : {v} (acceptée quand même)')
        return v

    @model_validator(mode='after')
    def calculer_nombre_mots(self):
        """Calculer automatiquement le nombre de mots."""
        if self.contenu and self.nombre_mots == 0:
            self.nombre_mots = len(self.contenu.split())
        return self


def valider_article(article_dict: dict) -> tuple:
    """Valider un article et retourner (article_valide, erreur)."""
    try:
        article = ArticleModel(**article_dict)
        return article, None
    except Exception as e:
        return None, str(e)


def valider_liste_articles(articles: list) -> tuple:
    """Valider une liste d'articles."""
    valides = []
    invalides = []

    for i, article in enumerate(articles):
        article_valide, erreur = valider_article(article)
        if article_valide:
            valides.append(article_valide.model_dump())
        else:
            invalides.append({
                'index': i,
                'url': article.get('url', '?'),
                'erreur': erreur
            })

    rapport = {
        'total': len(articles),
        'valides': len(valides),
        'invalides': len(invalides),
        'taux_validite': round(len(valides) / len(articles) * 100, 1) if articles else 0,
        'erreurs': invalides
    }

    return valides, rapport