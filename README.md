# Workflow IA — Guide Complet pour Débutants

Ce projet est un exemple structuré de workflow IA, conçu pour quelqu'un qui n'en a jamais créé.
Il traite un cas concret : **analyser un email entrant et générer une réponse automatique**.

## Structure du projet

```
Workflow/
├── README.md               # Ce fichier — guide général
├── config/
│   └── settings.json       # Configuration du workflow
├── prompts/
│   ├── classifier.md       # Prompt pour classifier l'email
│   └── responder.md        # Prompt pour générer la réponse
├── workflow/
│   ├── step1_input.py      # Etape 1 : recevoir et valider l'input
│   ├── step2_classify.py   # Etape 2 : classifier l'intention
│   ├── step3_respond.py    # Etape 3 : générer la réponse
│   └── step4_output.py     # Etape 4 : formater et envoyer l'output
├── main.py                 # Point d'entrée — orchestre tout le workflow
└── tests/
    └── test_workflow.py    # Tests des cas réels et limites
```

## Les 6 étapes de création d'un Workflow IA

### Etape 1 — Définir l'objectif

Avant d'écrire une seule ligne de code, répondre à ces questions :

| Question | Réponse pour ce projet |
|---|---|
| Quel est le déclencheur ? | Un email entrant |
| Quelle est la sortie ? | Une réponse email rédigée |
| Qui utilise ça ? | Un service client |
| Quelles contraintes ? | Réponse en < 3 secondes, ton professionnel |

### Etape 2 — Cartographier le flux de données

```
[Email entrant] 
    → Validation (est-ce un vrai email ?)
    → Classification (demande info / plainte / autre)
    → Génération réponse (selon la catégorie)
    → Formatage output (objet + corps du mail)
    → [Email de réponse prêt]
```

### Etape 3 — Choisir les composants IA

- **Claude** (via API Anthropic) pour la classification et la génération
- **Pas de mémoire long terme** nécessaire pour ce cas simple
- **Outils** : aucun outil externe (workflow autonome)

### Etape 4 — Concevoir les prompts (voir dossier `prompts/`)

Chaque étape IA a son propre prompt dédié dans `prompts/`.

### Etape 5 — Gérer les erreurs

- Input vide ou invalide → rejet avec message clair
- Catégorie inconnue → catégorie "autre" par défaut
- Erreur API → retry 3 fois, puis log et alerte

### Etape 6 — Tester

Lancer les tests : `python -m pytest tests/`

## Lancement rapide

```bash
# Installer les dépendances
pip install anthropic

# Configurer votre clé API
export ANTHROPIC_API_KEY="votre-clé-ici"

# Lancer le workflow avec un email exemple
python main.py
```
