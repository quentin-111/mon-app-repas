import streamlit as st
import requests
import google.generativeai as genai
from datetime import datetime, timedelta

# --- CONFIGURATION ---
DOC_ID_REGLES = "1-OL2ITtUqHv4ZksQ39SweU0fQXxkU-aKpy32_AsMshU"
DOC_ID_REPAS = "1JMQERJ2_KfqII45fZuXDyOATWLrbcwUM5sjRcOqt0YM"
MODEL_NAME = 'gemini-3-flash-preview'

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

def get_google_doc_text(doc_id):
    url = f"https://docs.google.com/document/d/{doc_id}/export?format=txt"
    try:
        response = requests.get(url)
        return response.text if response.status_code == 200 else "Erreur"
    except:
        return "Erreur"

# --- INTERFACE ---
st.set_page_config(page_title="Planning Repas Créatif", page_icon="📅")

st.title("📅 Planning Repas (2 semaines)")

# Zone de boutons
col1, col2 = st.columns(2)
with col1:
    generate_btn = st.button("🪄 Générer un nouveau planning", type="primary", use_container_width=True)
with col2:
    # Ce bouton fait techniquement la même chose mais l'IA génère toujours une réponse différente
    retry_btn = st.button("🔄 Refaire des propositions", use_container_width=True)

if generate_btn or retry_btn:
    with st.spinner("L'IA concocte de nouvelles idées inédites..."):
        regles = get_google_doc_text(DOC_ID_REGLES)
        historique = get_google_doc_text(DOC_ID_REPAS)
        
        try:
            model = genai.GenerativeModel(model_name=MODEL_NAME)
            
            prompt = f"""
            Tu es un chef créatif spécialisé dans la cuisine familiale saine.
            
            TES SOURCES (Style et Contraintes) :
            - Règles de vie : {regles}
            - Historique des plats aimés : {historique}
            
            MISSION :
            Génère un planning de 14 jours (du {datetime.now().strftime('%d/%m/%Y')} au {(datetime.now() + timedelta(days=13)).strftime('%d/%m/%Y')}).
            
            CONSIGNES DE CRÉATIVITÉ :
            - Ne recopie pas bêtement l'historique. Utilise-le pour comprendre les GOÛTS (ex: ils aiment les courges, les tartes, le végétarien).
            - Propose au moins 50% de NOUVELLES IDÉES de plats que l'on ne trouve pas dans l'historique, mais qui respectent le style (sain, rapide, saisonnier, enfant de 5 ans).
            - Varie les plaisirs : cuisine du monde (douce), gratins originaux, nouvelles façons de cuisiner les légumes d'hiver (panais, topinambours, poireaux, etc.).
            
            CONTRAINTES DE FORMAT :
            - Uniquement un TABLEAU Markdown : Jour, Date, Midi, Soir.
            - Pas de texte avant ou après.
            """
            
            response = model.generate_content(prompt)
            st.markdown(response.text)
            
        except Exception as e:
            st.error(f"Erreur : {e}")

st.divider()
st.info("Astuce : Si une idée ne vous plaît pas, cliquez sur 'Refaire des propositions' pour obtenir une version totalement différente.")
