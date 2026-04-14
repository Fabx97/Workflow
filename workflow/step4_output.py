"""
ETAPE 4 — Formatage et présentation de l'output

Rôle : Transformer le résultat brut de l'IA en une sortie
       exploitable par le système (ici : affichage ou envoi).
       C'est ici qu'on connecterait une vraie API email en production.
"""

from datetime import datetime


def formater_output(
    email_original: dict,
    classification: dict,
    reponse_generee: dict
) -> dict:
    """
    Assemble le résultat final du workflow.

    Args:
        email_original: l'email d'entrée validé
        classification: résultat de l'étape 2
        reponse_generee: résultat de l'étape 3

    Returns:
        dict complet représentant le résultat du workflow
    """
    return {
        "timestamp": datetime.now().isoformat(),
        "statut": "succes",
        "input": {
            "expediteur": email_original["expediteur"],
            "objet": email_original["objet"]
        },
        "analyse": {
            "categorie": classification["categorie"],
            "confiance": classification["confiance"],
            "resume": classification["resume"]
        },
        "reponse": {
            "destinataire": email_original["expediteur"],
            "objet": reponse_generee["objet"],
            "corps": reponse_generee["corps"]
        }
    }


def afficher_resultat(output: dict) -> None:
    """Affiche le résultat du workflow de manière lisible."""
    print("\n" + "="*60)
    print("RESULTAT DU WORKFLOW IA")
    print("="*60)

    print(f"\n[{output['timestamp']}]")
    print(f"Email de : {output['input']['expediteur']}")
    print(f"Sujet    : {output['input']['objet']}")

    print(f"\nANALYSE IA :")
    print(f"  Categorie : {output['analyse']['categorie']}")
    print(f"  Confiance : {output['analyse']['confiance'] * 100:.0f}%")
    print(f"  Resume    : {output['analyse']['resume']}")

    print(f"\nREPONSE GENEREE :")
    print(f"  Pour   : {output['reponse']['destinataire']}")
    print(f"  Objet  : {output['reponse']['objet']}")
    print(f"  Corps  :\n")
    for ligne in output['reponse']['corps'].split('\n'):
        print(f"    {ligne}")

    print("\n" + "="*60)
