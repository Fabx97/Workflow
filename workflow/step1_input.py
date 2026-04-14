"""
ETAPE 1 — Réception et validation de l'input

Rôle : S'assurer que les données qui entrent dans le workflow
       sont valides avant de faire appel à l'IA (économise des tokens).
"""


def validate_email(email: dict) -> dict:
    """
    Valide qu'un email a la structure attendue.

    Args:
        email: dict avec les clés 'expediteur', 'objet', 'corps'

    Returns:
        dict avec 'valide' (bool) et 'erreur' (str si invalide)
    """
    champs_requis = ["expediteur", "objet", "corps"]

    # Vérifier que tous les champs sont présents
    for champ in champs_requis:
        if champ not in email:
            return {"valide": False, "erreur": f"Champ manquant : '{champ}'"}

    # Vérifier que les champs ne sont pas vides
    for champ in champs_requis:
        if not email[champ] or not str(email[champ]).strip():
            return {"valide": False, "erreur": f"Champ vide : '{champ}'"}

    # Vérifier la longueur du corps (éviter les abus de tokens)
    if len(email["corps"]) > 5000:
        return {"valide": False, "erreur": "Corps de l'email trop long (max 5000 caractères)"}

    return {"valide": True, "erreur": None}


def formater_pour_ia(email: dict) -> str:
    """
    Formate l'email en texte clair pour l'envoyer à l'IA.

    Args:
        email: dict validé avec les clés de l'email

    Returns:
        str formaté prêt à insérer dans un prompt
    """
    return f"""De : {email['expediteur']}
Objet : {email['objet']}
Corps :
{email['corps']}"""
