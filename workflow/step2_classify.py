"""
ETAPE 2 — Classification de l'email

Rôle : Envoyer l'email à l'IA pour déterminer son intention.
       C'est la première vraie interaction avec le modèle.
"""

import json
import time
import anthropic
from pathlib import Path


def charger_prompt(nom_fichier: str) -> str:
    """Charge un prompt depuis le dossier prompts/."""
    chemin = Path(__file__).parent.parent / "prompts" / nom_fichier
    return chemin.read_text(encoding="utf-8")


def classifier_email(client: anthropic.Anthropic, email_formate: str, config: dict) -> dict:
    """
    Classifie l'email en appelant l'API Claude.

    Args:
        client: instance du client Anthropic
        email_formate: texte de l'email (produit par step1)
        config: configuration du workflow (depuis settings.json)

    Returns:
        dict avec 'categorie', 'confiance', 'resume'
    """
    system_prompt = charger_prompt("classifier.md")
    max_attempts = config["retry"]["max_attempts"]

    for tentative in range(max_attempts):
        try:
            reponse = client.messages.create(
                model=config["ai"]["model"],
                max_tokens=256,  # La classification ne nécessite pas beaucoup de tokens
                system=system_prompt,
                messages=[
                    {"role": "user", "content": f"Email à classifier :\n\n{email_formate}"}
                ]
            )

            # Extraire le JSON de la réponse
            texte_reponse = reponse.content[0].text.strip()
            resultat = json.loads(texte_reponse)

            # Valider que les champs attendus sont présents
            assert "categorie" in resultat
            assert "confiance" in resultat
            assert "resume" in resultat

            return resultat

        except (json.JSONDecodeError, AssertionError, KeyError) as e:
            # L'IA n'a pas respecté le format JSON demandé
            if tentative < max_attempts - 1:
                time.sleep(config["retry"]["delay_seconds"])
                continue
            # Après tous les essais, retourner une catégorie par défaut
            return {
                "categorie": "autre",
                "confiance": 0.0,
                "resume": f"Erreur de classification après {max_attempts} tentatives"
            }
