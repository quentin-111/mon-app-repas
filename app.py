import streamlit as st
import requests
import google.generativeai as genai
from datetime import datetime

# --- CONFIGURATION ---
# Remplace par tes IDs de documents
DOC_ID_REGLES = "1-OL2ITtUqHv4ZksQ39SweU0fQXxkU-aKpy32_AsMshU"
DOC_ID_REPAS = "1JMQERJ2_KfqII45fZuXDyOATWLrbcwUM5sjRcOqt0YM"

# Configuration Gemini (La clé sera gérée dans les secrets Streamlit plus tard)
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("Clé API non configurée dans les secrets.")

def get_google_doc_text(doc_id):
    url = f"https://docs.google.com/document/d/{doc_id}/export?format=txt"
    response = requests.get(url)
    return response.text if response.status_code == 200 else "Erreur de lecture"

# --- INTERFACE ---
st.set_page_config(page_title="Menu de la Maison", page_icon="🥗")

st.title("🍽️ Qu'est-ce qu'on mange ?")
st.write(f"Aujourd'hui, nous sommes le **{datetime.now().strftime('%A %d %B %Y')}**")

if st.button("Générer une suggestion de repas", type="primary"):
    with st.spinner("Je consulte tes règles et tes goûts..."):
        # 1. Récupération des données
        regles = get_google_doc_text(DOC_ID_REGLES)
        historique = get_google_doc_text(DOC_ID_REPAS)
        
        # 2. Préparation du modèle
        model = genai.GenerativeModel('gemini-1.5-flash') # Version rapide et efficace
        
        prompt = f"""
        Tu es un assistant culinaire familial. 
        Voici mes RÈGLES DE VIE (Planning, courses, contraintes enfant) :
        {regles}
        
        Voici mon HISTORIQUE DE REPAS (pour t'inspirer de nos goûts) :
        {historique}
        
        CONTEXTE ACTUEL :
        - Nous sommes le : {datetime.now().strftime('%A %d %B')}
        - Lieu : Région Parisienne, France.
        
        MISSION :
        Suggère-moi le(s) repas pertinent(s) pour AUJOURD'HUI uniquement.
        - Si c'est un jour de semaine : propose le repas du soir.
        - Si c'est samedi : propose midi ET soir.
        - Si c'est dimanche : propose le midi uniquement.
        
        CONSIGNES IMPORTANTES :
        1. Respecte la saisonnalité (France).
        2. Respecte scrupuleusement les contraintes de temps de préparation.
        3. Pas d'épices fortes ni d'ail (pour l'enfant de 5 ans).
        4. Vérifie la règle du marché du dimanche pour le samedi.
        5. Sois concis et chaleureux.
        """
        
        # 3. Génération
        response = model.generate_content(prompt)
        
        st.success("Voici ma suggestion :")
        st.markdown(response.text)

st.divider()
st.info("Modifier les [Règles](https://docs.google.com/document/d/1-OL2ITtUqHv4ZksQ39SweU0fQXxkU-aKpy32_AsMshU/edit) ou les [Exemples](https://docs.google.com/document/d/1JMQERJ2_KfqII45fZuXDyOATWLrbcwUM5sjRcOqt0YM/edit)")
