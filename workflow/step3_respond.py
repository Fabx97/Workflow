"""
ETAPE 3 — Génération de la réponse

Rôle : En utilisant la catégorie détectée à l'étape 2,
       demander à l'IA de rédiger une réponse appropriée.
"""

import json
import time
import anthropic
from pathlib import Path


def charger_prompt(nom_fichier: str) -> str:
    """Charge un prompt depuis le dossier prompts/."""
    chemin = Path(__file__).parent.parent / "prompts" / nom_fichier
    return chemin.read_text(encoding="utf-8")


def generer_reponse(
    client: anthropic.Anthropic,
    email_formate: str,
    classification: dict,
    config: dict
) -> dict:
    """
    Génère une réponse email adaptée à la catégorie détectée.

    Args:
        client: instance du client Anthropic
        email_formate: texte original de l'email
        classification: résultat de l'étape 2 (catégorie, résumé...)
        config: configuration du workflow

    Returns:
        dict avec 'objet' et 'corps' de la réponse
    """
    system_prompt = charger_prompt("responder.md")
    max_attempts = config["retry"]["max_attempts"]

    # Construire le message utilisateur avec le contexte complet
    message_utilisateur = f"""Email original :
{email_formate}

Catégorie détectée : {classification['categorie']}
Résumé : {classification['resume']}

Génère une réponse appropriée."""

    for tentative in range(max_attempts):
        try:
            reponse = client.messages.create(
                model=config["ai"]["model"],
                max_tokens=config["ai"]["max_tokens"],
                system=system_prompt,
                messages=[
                    {"role": "user", "content": message_utilisateur}
                ]
            )

            texte_reponse = reponse.content[0].text.strip()
            resultat = json.loads(texte_reponse)

            assert "objet" in resultat
            assert "corps" in resultat

            return resultat

        except (json.JSONDecodeError, AssertionError, KeyError):
            if tentative < max_attempts - 1:
                time.sleep(config["retry"]["delay_seconds"])
                continue
            # Réponse de secours générique
            return {
                "objet": "Re: Votre message",
                "corps": "Bonjour,\n\nNous avons bien reçu votre message et nous vous répondrons dans les plus brefs délais.\n\nCordialement,\nL'équipe Support"
            }
