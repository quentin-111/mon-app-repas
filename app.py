import streamlit as st
import requests
import google.generativeai as genai
from datetime import datetime

# --- CONFIGURATION DES DOCUMENTS ---
# Tes IDs de documents vérifiés
DOC_ID_REGLES = "1-OL2ITtUqHv4ZksQ39SweU0fQXxkU-aKpy32_AsMshU"
DOC_ID_REPAS = "1JMQERJ2_KfqII45fZuXDyOATWLrbcwUM5sjRcOqt0YM"

# Nom exact du modèle pour Gemini 3
MODEL_NAME = 'gemini-3-flash-preview'

# Configuration de la sécurité et de l'API
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    else:
        st.error("Erreur : La clé GEMINI_API_KEY est manquante dans les secrets Streamlit.")
except Exception as e:
    st.error(f"Erreur de configuration : {e}")

def get_google_doc_text(doc_id):
    """Récupère le contenu d'un Google Doc public en texte brut."""
    url = f"https://docs.google.com/document/d/{doc_id}/export?format=txt"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return f"Erreur de lecture (Code {response.status_code})"
    except Exception as e:
        return f"Erreur de connexion : {e}"

# --- INTERFACE UTILISATEUR ---
st.set_page_config(page_title="Menu Maison", page_icon="🥗", layout="centered")

st.title("🍽️ Notre Assistant Repas")
st.write(f"Aujourd'hui : **{datetime.now().strftime('%A %d %B %Y')}**")

if st.button("🪄 Suggérer un repas", type="primary"):
    with st.spinner("Analyse des règles et de l'historique..."):
        # 1. Récupération des données en direct
        regles_brutes = get_google_doc_text(DOC_ID_REGLES)
        historique_brut = get_google_doc_text(DOC_ID_REPAS)
        
        # 2. Vérification de sécurité
        if "Erreur" in regles_brutes or len(regles_brutes) < 50:
            st.error("⚠️ Impossible de lire vos règles. Vérifiez que le Google Doc est bien partagé en 'Tous les utilisateurs disposant du lien'.")
        else:
            try:
                # 3. Initialisation du modèle Gemini 3
                model = genai.GenerativeModel(model_name=MODEL_NAME)
                
                # 4. Construction du prompt ultra-précis
                prompt = f"""
                Tu es un expert en organisation de repas familiaux. 
                Utilise exclusivement les informations suivantes pour répondre :
                
                MES RÈGLES DE VIE : 
                {regles_brutes}
                
                MON HISTORIQUE ET MES GOÛTS : 
                {historique_brut}
                
                CONTEXTE TEMPOREL : 
                Nous sommes aujourd'hui le {datetime.now().strftime('%A %d %B %Y')}.
                Lieu : Région Parisienne, France.
                
                TA MISSION :
                Propose le(s) repas idéal/idéaux pour AUJOURD'HUI.
                - Respecte le jour de la semaine et si c'est le midi ou le soir (selon mes règles).
                - Respecte scrupuleusement la règle du marché du dimanche et de la conservation des légumes.
                - Propose quelque chose qui convient à un enfant de 5 ans (pas d'ail, pas d'épices).
                - Sois cohérent avec la saison en France.
                - Présente ta réponse de manière chaleureuse et structurée (Ingrédients principaux + Pourquoi ce choix).
                """
                
                # 5. Appel à l'IA
                response = model.generate_content(prompt)
                
                st.success("Voici ma suggestion :")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"Désolé, une erreur technique est survenue : {e}")
                st.info(f"Modèle utilisé : {MODEL_NAME}")

st.divider()
st.caption("Données sources :")
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"[📄 Voir les Règles](https://docs.google.com/document/d/{DOC_ID_REGLES}/edit)")
with col2:
    st.markdown(f"[📋 Voir les Exemples](https://docs.google.com/document/d/{DOC_ID_REPAS}/edit)")
