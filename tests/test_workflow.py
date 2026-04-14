"""
TESTS — Vérifier que chaque étape fonctionne correctement

Rôle : Tester les cas normaux ET les cas limites (inputs vides,
       formats invalides, etc.) SANS appeler l'API (pas de coût).

Usage :
    python -m pytest tests/ -v
"""

import sys
from pathlib import Path

# Ajouter la racine du projet au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from workflow.step1_input import validate_email, formater_pour_ia
from workflow.step4_output import formater_output


class TestEtape1Validation:
    """Tests pour la validation des emails entrants."""

    def test_email_valide(self):
        email = {
            "expediteur": "test@exemple.fr",
            "objet": "Question",
            "corps": "Bonjour, j'ai une question."
        }
        resultat = validate_email(email)
        assert resultat["valide"] is True
        assert resultat["erreur"] is None

    def test_champ_manquant(self):
        email = {"expediteur": "test@exemple.fr", "objet": "Question"}
        # 'corps' est manquant
        resultat = validate_email(email)
        assert resultat["valide"] is False
        assert "corps" in resultat["erreur"]

    def test_champ_vide(self):
        email = {
            "expediteur": "test@exemple.fr",
            "objet": "",  # Vide !
            "corps": "Bonjour"
        }
        resultat = validate_email(email)
        assert resultat["valide"] is False
        assert "objet" in resultat["erreur"]

    def test_corps_trop_long(self):
        email = {
            "expediteur": "test@exemple.fr",
            "objet": "Test",
            "corps": "x" * 6000  # Dépasse la limite de 5000 caractères
        }
        resultat = validate_email(email)
        assert resultat["valide"] is False
        assert "trop long" in resultat["erreur"]

    def test_formatage_pour_ia(self):
        email = {
            "expediteur": "test@exemple.fr",
            "objet": "Ma question",
            "corps": "Bonjour, je voulais savoir..."
        }
        texte = formater_pour_ia(email)
        assert "test@exemple.fr" in texte
        assert "Ma question" in texte
        assert "je voulais savoir" in texte


class TestEtape4Output:
    """Tests pour le formatage de l'output final."""

    def test_output_structure(self):
        email = {"expediteur": "a@b.fr", "objet": "Test", "corps": "Corps"}
        classification = {"categorie": "information", "confiance": 0.9, "resume": "Une question"}
        reponse = {"objet": "Re: Test", "corps": "Bonjour, voici la réponse."}

        output = formater_output(email, classification, reponse)

        assert output["statut"] == "succes"
        assert "timestamp" in output
        assert output["analyse"]["categorie"] == "information"
        assert output["reponse"]["destinataire"] == "a@b.fr"

    def test_output_contient_toutes_les_cles(self):
        email = {"expediteur": "x@y.fr", "objet": "Sujet", "corps": "Corps"}
        classification = {"categorie": "plainte", "confiance": 0.8, "resume": "Insatisfaction"}
        reponse = {"objet": "Re: Sujet", "corps": "Nous sommes désolés..."}

        output = formater_output(email, classification, reponse)

        # Vérifier la structure complète
        assert "timestamp" in output
        assert "statut" in output
        assert "input" in output
        assert "analyse" in output
        assert "reponse" in output
