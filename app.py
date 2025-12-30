import streamlit as st
import requests
import google.generativeai as genai
from datetime import datetime, timedelta

# --- CONFIGURATION ---
DOC_ID_REGLES = "1-OL2ITtUqHv4ZksQ39SweU0fQXxkU-aKpy32_AsMshU"
DOC_ID_REPAS = "1JMQERJ2_KfqII45fZuXDyOATWLrbcwUM5sjRcOqt0YM"
MODEL_NAME = 'gemini-3-flash-preview'

try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error(f"Erreur API : {e}")

def get_google_doc_text(doc_id):
    url = f"https://docs.google.com/document/d/{doc_id}/export?format=txt"
    try:
        response = requests.get(url)
        return response.text if response.status_code == 200 else "Erreur"
    except:
        return "Erreur"

# --- INTERFACE ---
st.set_page_config(page_title="Planning Repas", page_icon="📅")

st.title("📅 Planning des 2 prochaines semaines")
st.write(f"Généré le **{datetime.now().strftime('%d/%m/%Y')}**")

if st.button("🪄 Générer le planning complet", type="primary"):
    with st.spinner("Planification en cours..."):
        regles = get_google_doc_text(DOC_ID_REGLES)
        historique = get_google_doc_text(DOC_ID_REPAS)
        
        try:
            model = genai.GenerativeModel(model_name=MODEL_NAME)
            
            # Prompt modifié pour un planning de 14 jours sans blabla
            prompt = f"""
            Tu es un planificateur de repas expert. 
            RÈGLES : {regles}
            HISTORIQUE : {historique}
            
            MISSION :
            Génère un planning de repas pour les 14 PROCHAINS JOURS à partir d'aujourd'hui ({datetime.now().strftime('%A %d %B %Y')}).
            
            CONTRAINTES DE FORMAT :
            1. Réponds UNIQUEMENT sous forme de TABLEAU Markdown.
            2. Colonnes : Jour, Date, Repas Midi, Repas Soir.
            3. Si un créneau ne nécessite pas de repas selon les règles (ex: midi en semaine), laisse la case vide ou mets "-".
            4. Ne donne AUCUNE explication, AUCUN ingrédient, AUCUNE introduction. Juste le tableau.
            
            RÈGLES MÉTIER À RESPECTER :
            - Samedi : Midi et Soir.
            - Dimanche : Midi uniquement.
            - Semaine : Soir uniquement.
            - Jeudi : Pâtes légumes obligatoires.
            - Respecte la saisonnalité (Hiver actuel) et la règle du marché/conservation.
            - Alterne les plats de l'historique pour varier.
            """
            
            response = model.generate_content(prompt)
            
            # Affichage du tableau
            st.markdown(response.text)
            
            st.success("Planning généré ! Tu peux faire une capture d'écran ou le copier.")

        except Exception as e:
            st.error(f"Erreur : {e}")

st.divider()
st.info("Les suggestions se basent sur vos documents Google Docs en temps réel.")
