"""
Interface Streamlit — Workflow IA Email Auto-Responder

Lancement :
    streamlit run app.py
"""

import os
import streamlit as st

from main import executer_workflow

# ── Configuration de la page ─────────────────────────────────────────────────

st.set_page_config(
    page_title="Workflow IA — Email Auto-Responder",
    page_icon="✉️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS personnalisé ──────────────────────────────────────────────────────────

st.markdown("""
<style>
/* Barre latérale */
[data-testid="stSidebar"] { background-color: #0f1117; }

/* Badges de catégorie */
.badge {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.85rem;
    letter-spacing: 0.03em;
}
.badge-information { background: #1a3a5c; color: #60a5fa; }
.badge-plainte     { background: #3b1a1a; color: #f87171; }
.badge-commande    { background: #1a3b1a; color: #4ade80; }
.badge-autre       { background: #2a2a2a; color: #94a3b8; }

/* Boîte de réponse générée */
.response-box {
    background: #1e2130;
    border: 1px solid #2d3149;
    border-radius: 10px;
    padding: 20px 24px;
    font-family: monospace;
    font-size: 0.9rem;
    white-space: pre-wrap;
    line-height: 1.6;
    color: #e2e8f0;
}

/* Indicateurs d'étapes */
.step { display: flex; align-items: flex-start; gap: 12px; margin-bottom: 12px; }
.step-icon { font-size: 1.2rem; min-width: 28px; text-align: center; }
.step-text { font-size: 0.9rem; color: #94a3b8; padding-top: 2px; }
.step-text.ok  { color: #4ade80; }
.step-text.err { color: #f87171; }
.step-text.run { color: #facc15; }

/* Barre de confiance */
.conf-bar-bg  { background:#2d3149; border-radius:6px; height:8px; margin-top:6px; }
.conf-bar-fg  { border-radius:6px; height:8px; }
</style>
""", unsafe_allow_html=True)


# ── Sidebar — Configuration ───────────────────────────────────────────────────

with st.sidebar:
    st.title("⚙️ Configuration")
    st.divider()

    api_key_input = st.text_input(
        "Clé API Anthropic",
        type="password",
        value=os.environ.get("ANTHROPIC_API_KEY", ""),
        placeholder="sk-ant-...",
        help="Disponible sur console.anthropic.com",
    )

    st.divider()
    st.caption("**À propos du workflow**")
    st.caption(
        "Ce workflow analyse un email entrant en **4 étapes** :\n\n"
        "1. Validation\n"
        "2. Classification IA\n"
        "3. Génération réponse IA\n"
        "4. Formatage output"
    )
    st.divider()
    st.caption("Modèle : `claude-sonnet-4-6`")


# ── Titre principal ───────────────────────────────────────────────────────────

st.title("✉️ Workflow IA — Email Auto-Responder")
st.caption("Saisissez un email reçu. L'IA va l'analyser et rédiger une réponse adaptée automatiquement.")
st.divider()

# ── Layout : 2 colonnes ───────────────────────────────────────────────────────

col_input, col_result = st.columns([1, 1], gap="large")

# ── Colonne gauche : Formulaire d'entrée ─────────────────────────────────────

with col_input:
    st.subheader("📥 Email entrant")

    with st.form("email_form"):
        expediteur = st.text_input(
            "Expéditeur",
            placeholder="client@exemple.fr",
        )
        objet = st.text_input(
            "Objet",
            placeholder="Problème avec ma commande #45123",
        )
        corps = st.text_area(
            "Corps de l'email",
            placeholder="Bonjour,\n\nJ'ai un problème avec...",
            height=220,
        )

        st.divider()
        col_demo, col_submit = st.columns([1, 1])
        with col_demo:
            charger_demo = st.form_submit_button("🔄 Charger démo", use_container_width=True)
        with col_submit:
            lancer = st.form_submit_button(
                "🚀 Lancer le workflow",
                type="primary",
                use_container_width=True,
            )

# Données de démo
DEMO = {
    "expediteur": "marie.dupont@exemple.fr",
    "objet": "Problème avec ma commande #45123",
    "corps": (
        "Bonjour,\n\n"
        "J'ai passé une commande il y a 10 jours (numéro #45123) et je n'ai toujours "
        "rien reçu. Le suivi de livraison indique que le colis est \"en transit\" depuis "
        "une semaine sans mise à jour.\n\n"
        "Je suis très déçue par ce manque de communication. Pourriez-vous me dire "
        "où en est ma commande ?\n\n"
        "Merci,\nMarie Dupont"
    ),
}

# Injection des données de démo via session_state
if charger_demo:
    st.session_state["demo_loaded"] = True
    st.rerun()

if st.session_state.get("demo_loaded"):
    expediteur = DEMO["expediteur"]
    objet = DEMO["objet"]
    corps = DEMO["corps"]
    # On réaffiche les valeurs mais on ne relance pas automatiquement


# ── Colonne droite : Progression + Résultats ─────────────────────────────────

with col_result:
    st.subheader("📊 Résultats")

    ETAPES = [
        "Validation de l'email",
        "Classification IA",
        "Génération de la réponse",
        "Formatage du résultat",
    ]

    if lancer:
        # Vérifications préalables côté UI
        if not api_key_input:
            st.error("Clé API manquante — renseignez-la dans la barre latérale.")
            st.stop()
        if not expediteur or not objet or not corps:
            st.error("Tous les champs sont requis.")
            st.stop()

        os.environ["ANTHROPIC_API_KEY"] = api_key_input

        email = {"expediteur": expediteur, "objet": objet, "corps": corps}

        # Zones dynamiques pour la progression et le résultat
        progress_container = st.container()
        result_placeholder = st.empty()

        # État de progression affiché en temps réel
        etapes_statut = {i: "pending" for i in range(1, 5)}
        etapes_msg    = {i: ETAPES[i - 1] for i in range(1, 5)}

        def render_steps(statuts, messages):
            icons = {"pending": "⬜", "running": "🔄", "ok": "✅", "erreur": "❌"}
            css   = {"pending": "", "running": "run", "ok": "ok", "erreur": "err"}
            html  = ""
            for i in range(1, 5):
                s = statuts[i]
                html += (
                    f'<div class="step">'
                    f'<span class="step-icon">{icons[s]}</span>'
                    f'<span class="step-text {css[s]}"><strong>Etape {i}</strong> — {messages[i]}</span>'
                    f'</div>'
                )
            return html

        steps_placeholder = progress_container.empty()
        steps_placeholder.markdown(render_steps(etapes_statut, etapes_msg), unsafe_allow_html=True)

        def on_progress(etape, message, statut):
            etapes_statut[etape] = statut
            etapes_msg[etape] = message
            steps_placeholder.markdown(render_steps(etapes_statut, etapes_msg), unsafe_allow_html=True)

        # Lancement du workflow
        with st.spinner(""):
            try:
                output = executer_workflow(email, on_progress=on_progress)
            except EnvironmentError as e:
                st.error(str(e))
                st.stop()
            except Exception as e:
                st.error(f"Erreur inattendue : {e}")
                st.stop()

        if output.get("statut") == "erreur":
            st.error(f"Workflow échoué : {output.get('message')}")
            st.stop()

        # ── Affichage des résultats ───────────────────────────────────────────
        st.divider()

        # Catégorie + confiance
        cat       = output["analyse"]["categorie"]
        confiance = output["analyse"]["confiance"]
        resume    = output["analyse"]["resume"]

        badge_class = f"badge-{cat}" if cat in ("information", "plainte", "commande") else "badge-autre"

        col_cat, col_conf = st.columns([1, 1])
        with col_cat:
            st.caption("CATÉGORIE DÉTECTÉE")
            st.markdown(
                f'<span class="badge {badge_class}">{cat.upper()}</span>',
                unsafe_allow_html=True,
            )
        with col_conf:
            st.caption("CONFIANCE IA")
            pct = int(confiance * 100)
            color = "#4ade80" if pct >= 80 else "#facc15" if pct >= 50 else "#f87171"
            st.markdown(
                f"**{pct}%**"
                f'<div class="conf-bar-bg"><div class="conf-bar-fg" style="width:{pct}%;background:{color};"></div></div>',
                unsafe_allow_html=True,
            )

        st.caption(f"_{resume}_")
        st.divider()

        # Réponse générée
        st.caption("RÉPONSE GÉNÉRÉE")
        objet_rep = output["reponse"]["objet"]
        corps_rep  = output["reponse"]["corps"]

        st.markdown(f"**Objet :** `{objet_rep}`")
        st.markdown(
            f'<div class="response-box">{corps_rep}</div>',
            unsafe_allow_html=True,
        )

        st.text_area(
            "Copier la réponse",
            value=corps_rep,
            height=140,
            label_visibility="collapsed",
        )
        st.caption("☝️ Sélectionnez le texte ci-dessus pour copier")

    else:
        # État initial — instructions
        st.info(
            "**Comment utiliser ce workflow :**\n\n"
            "1. Renseignez votre **clé API** dans la barre latérale\n"
            "2. Saisissez un email dans le formulaire (ou chargez la **démo**)\n"
            "3. Cliquez sur **Lancer le workflow**\n\n"
            "L'IA va analyser l'email et générer une réponse en quelques secondes.",
            icon="💡",
        )

        st.divider()
        st.caption("**Catégories gérées**")
        cols = st.columns(4)
        categories = [
            ("information", "badge-information", "Demande de renseignements"),
            ("plainte",     "badge-plainte",     "Insatisfaction / problème"),
            ("commande",    "badge-commande",    "Suivi de commande"),
            ("autre",       "badge-autre",       "Autre demande"),
        ]
        for col, (label, css, desc) in zip(cols, categories):
            with col:
                st.markdown(f'<span class="badge {css}">{label}</span>', unsafe_allow_html=True)
                st.caption(desc)
