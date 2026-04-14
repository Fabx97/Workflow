"""
POINT D'ENTREE — Orchestrateur du workflow

Rôle : Appeler chaque étape dans l'ordre et passer les données
       d'une étape à l'autre. C'est le "chef d'orchestre".

Usage :
    python main.py
"""

import json
import os
from pathlib import Path

import anthropic

# Importer chaque étape du workflow
from workflow.step1_input import validate_email, formater_pour_ia
from workflow.step2_classify import classifier_email
from workflow.step3_respond import generer_reponse
from workflow.step4_output import formater_output, afficher_resultat


def charger_config() -> dict:
    """Charge la configuration depuis config/settings.json."""
    chemin = Path(__file__).parent / "config" / "settings.json"
    with open(chemin, encoding="utf-8") as f:
        return json.load(f)


def executer_workflow(email: dict, on_progress=None) -> dict:
    """
    Exécute le workflow complet sur un email.

    Args:
        email: dict avec 'expediteur', 'objet', 'corps'
        on_progress: callback optionnel appelé à chaque étape.
                     Signature : on_progress(etape: int, message: str, statut: str)
                     statut peut être "running" | "ok" | "erreur"

    Returns:
        dict avec le résultat complet du workflow
    """
    def notifier(etape, message, statut="running"):
        if on_progress:
            on_progress(etape, message, statut)
        else:
            print(f"Etape {etape}/4 : {message}")

    config = charger_config()

    # Initialiser le client Anthropic (une seule fois pour tout le workflow)
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "La variable d'environnement ANTHROPIC_API_KEY n'est pas définie."
        )

    client = anthropic.Anthropic(api_key=api_key)

    # --- ETAPE 1 : Validation de l'input ---
    notifier(1, "Validation de l'email...", "running")
    validation = validate_email(email)
    if not validation["valide"]:
        notifier(1, f"Email invalide — {validation['erreur']}", "erreur")
        return {"statut": "erreur", "message": validation["erreur"]}
    email_formate = formater_pour_ia(email)
    notifier(1, "Email validé", "ok")

    # --- ETAPE 2 : Classification ---
    notifier(2, "Classification de l'intention...", "running")
    classification = classifier_email(client, email_formate, config)
    notifier(2, f"Catégorie : {classification['categorie']} ({classification['confiance']*100:.0f}% confiance)", "ok")

    # --- ETAPE 3 : Génération de la réponse ---
    notifier(3, "Génération de la réponse...", "running")
    reponse = generer_reponse(client, email_formate, classification, config)
    notifier(3, "Réponse générée", "ok")

    # --- ETAPE 4 : Formatage de l'output ---
    notifier(4, "Assemblage du résultat...", "running")
    output = formater_output(email, classification, reponse)
    notifier(4, "Workflow terminé", "ok")

    return output


# --- EMAIL DE DÉMONSTRATION ---
# Modifiez cet email pour tester différents scénarios
EMAIL_DEMO = {
    "expediteur": "marie.dupont@exemple.fr",
    "objet": "Problème avec ma commande #45123",
    "corps": """Bonjour,

J'ai passé une commande il y a 10 jours (numéro #45123) et je n'ai toujours
rien reçu. Le suivi de livraison indique que le colis est "en transit" depuis
une semaine sans mise à jour.

Je suis très déçue par ce manque de communication. Pourriez-vous me dire
où en est ma commande ?

Merci,
Marie Dupont"""
}


if __name__ == "__main__":
    resultat = executer_workflow(EMAIL_DEMO)
    afficher_resultat(resultat)
