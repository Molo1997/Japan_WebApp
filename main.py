import streamlit as st
import folium
from streamlit_folium import st_folium 
from folium import plugins
from datetime import datetime
import pytz 
import pandas as pd
import json
import os
from pathlib import Path
import random
from PIL import Image
from supabase import create_client

# Supabase configuration
SUPABASE_URL = st.secrets["supabase_url"]  
SUPABASE_KEY = st.secrets["supabase_key"]

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing Supabase credentials. Please check secrets.toml")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configurazione pagina
st.set_page_config(
    page_title="Viaggio in Giappone",
    page_icon="🗾",
    layout="wide",
    initial_sidebar_state="expanded"
)

JAPAN_CITIES = {
    "Tokyo": {"lat": 35.6762, "lon": 139.6503},
    "Kyoto": {"lat": 35.0116, "lon": 135.7681},
    "Osaka": {"lat": 34.6937, "lon": 135.5023},
    "Nara": {"lat": 34.6851, "lon": 135.8048},
    "Hiroshima": {"lat": 34.3853, "lon": 132.4553},
    "Sapporo": {"lat": 43.0618, "lon": 141.3545},
    "Fukuoka": {"lat": 33.5902, "lon": 130.4017},
    "Kanazawa": {"lat": 36.5944, "lon": 136.6255},
    "Nagoya": {"lat": 35.1815, "lon": 136.9066},
    "Kobe": {"lat": 34.6901, "lon": 135.1955},
    "Takayama": {"lat": 36.1408, "lon": 137.2520},
    "Hakone": {"lat": 35.2324, "lon": 139.1069},
    "Nikko": {"lat": 36.7198, "lon": 139.6982},
    "Kamakura": {"lat": 35.3192, "lon": 139.5467},
    "Matsumoto": {"lat": 36.2384, "lon": 137.9720},
    "Kawaguchiko": {"lat": 35.5171, "lon": 138.7510},
    "Himeji": {"lat": 34.8157, "lon": 134.6854},
    "Ise": {"lat": 34.4873, "lon": 136.7257},
    "Sendai": {"lat": 38.2682, "lon": 140.8694},
    "Nagasaki": {"lat": 32.7503, "lon": 129.8777},
    "Yokohama": {"lat": 35.4437, "lon": 139.6380},
    "Takeshima": {"lat": 34.2891, "lon": 133.0182},
    "Miyajima": {"lat": 34.2971, "lon": 132.3197},
    "Koyasan": {"lat": 34.2130, "lon": 135.5855}
}

class DatabaseManager:
    def __init__(self):
        self.supabase = supabase
        
    def get_trip_data(self, trip_id: str = "default_trip"):
        try:
            response = self.supabase.table('trips').select("*").eq('id', trip_id).execute()
            return response.data[0]['data'] if response.data else self.create_empty_data()
        except Exception as e:
            st.error(f"Errore nel caricamento dei dati: {str(e)}")
            return self.create_empty_data()
    
    def save_trip_data(self, data: dict, trip_id: str = "default_trip"):
        try:
            data["meta"] = {
                "ultima_modifica": datetime.now(pytz.timezone('Europe/Rome')).strftime('%Y-%m-%d %H:%M:%S'),
                "ultima_modifica_utente": "user",
                "versione_dati": "1.0"
            }
            
            response = self.supabase.table('trips').upsert({
                'id': trip_id,
                'data': data,
                'updated_at': datetime.now().isoformat()
            }).execute()
            
            return True if response.data else False
        except Exception as e:
            st.error(f"Errore nel salvataggio dei dati: {str(e)}")
            return False
            
    def save_city_data(self, city_name: str, data: dict, trip_id: str = "default_trip"):
        try:
            response = self.supabase.table('cities').upsert({
                'trip_id': trip_id,
                'city_name': city_name,
                'data': data,
                'updated_at': datetime.now().isoformat()
            }).execute()
            return True if response.data else False
        except Exception as e:
            st.error(f"Errore nel salvataggio dati città: {str(e)}")
            return False

    def get_city_data(self, city_name: str, trip_id: str = "default_trip"):
        try:
            response = self.supabase.table('cities') \
                .select("*") \
                .eq('trip_id', trip_id) \
                .eq('city_name', city_name) \
                .execute()
            return response.data[0]['data'] if response.data else self.get_empty_city_structure()
        except Exception as e:
            st.error(f"Errore nel caricamento dati città: {str(e)}")
            return self.get_empty_city_structure()

    def create_empty_data(self):
        return {
            "costi_partenza": {
                "voli": [],
                "assicurazioni": [],
                "altro": [],
                "totale_generale": 0
            },
            "dati_citta": {},
            "budget": {
                "totale_pianificato": 0,
                "speso_corrente": 0,
                "rimanente": 0,
                "suddivisione_per_categoria": {
                    "alloggi": 0,
                    "ristoranti": 0,
                    "negozi": 0,
                    "attivita": 0,
                    "trasporti": 0
                }
            },
            "custom_gallery_link": "",  
            "meta": {
                "ultima_modifica": datetime.now(pytz.timezone('Europe/Rome')).strftime('%Y-%m-%d %H:%M:%S'),
                "ultima_modifica_utente": "system",
                "versione_dati": "1.0"
            }
        }

    def get_empty_city_structure(self):
        """Restituisce la struttura vuota per una nuova città"""
        return {
            "alloggi": {},
            "ristoranti": {},
            "negozi": {},
            "attivita": {},
            "trasporti": {},
            "coordinate": {
                "lat": 0,
                "lon": 0
            }
        }

# Initialize database connection
db = DatabaseManager()

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = db.get_trip_data()

# Funzioni di input
def input_accommodation_section():
    """Gestisce la sezione input per gli alloggi"""
    st.subheader("🏨 Alloggi")
    accommodations = {}
    accommodation_key = "alloggio_1"
    accommodations[accommodation_key] = {}
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Informazioni della struttura e prenotazione
        accommodations[accommodation_key]["nome"] = st.text_input("Nome struttura")
        accommodations[accommodation_key]["tipo"] = st.selectbox(
            "Tipo", 
            ["Hotel", "Ryokan", "Capsule", "Ostello", "Altro"]
        )
        accommodations[accommodation_key]["indirizzo"] = st.text_input("Indirizzo completo")
        accommodations[accommodation_key]["link_booking"] = st.text_input("Link Booking/Struttura")
        accommodations[accommodation_key]["numero_conferma"] = st.text_input("Numero di conferma")
        accommodations[accommodation_key]["codice_pin"] = st.text_input("Codice PIN")
    
    with col2:
        # Informazioni temporali e costi
        check_in_date = st.date_input("Data Check-in")
        accommodations[accommodation_key]["check_in_date"] = check_in_date.strftime("%d-%m-%Y")
        accommodations[accommodation_key]["orario_check_in"] = st.text_input("Orario Check-in (es. 16:00 - 19:30)")
        check_out_date = st.date_input("Data Check-out")
        accommodations[accommodation_key]["check_out_date"] = check_out_date.strftime("%d-%m-%Y")
        accommodations[accommodation_key]["orario_check_out"] = st.text_input("Orario Check-out (es. 06:30 - 10:00)")
        accommodations[accommodation_key]["notti"] = st.number_input("Numero notti", min_value=1, step=1)
        accommodations[accommodation_key]["costo"] = st.number_input("Costo totale (€)", min_value=0.0, step=10.0)
    
    # Note alla fine
    accommodations[accommodation_key]["note"] = st.text_area("Note aggiuntive")
    
    return accommodations

def input_restaurants_section():
    """Gestisce la sezione input per i ristoranti"""
    st.subheader("🍜 Ristoranti")
    restaurants = {}
    restaurant_key = "ristorante_1"
    restaurants[restaurant_key] = {}
    
    col1, col2 = st.columns(2)
    
    with col1:
        restaurants[restaurant_key]["nome"] = st.text_input("Nome ristorante")
        restaurants[restaurant_key]["tipo"] = st.selectbox(
            "Tipo cucina", 
            ["Tradizionale", "Ramen", "Sushi", "Izakaya", "Street Food", "Teppanyaki", "Altro"]
        )
        restaurants[restaurant_key]["quartiere"] = st.text_input("Quartiere")
        restaurants[restaurant_key]["stazione"] = st.text_input("Stazione più vicina")
    
    with col2:
        orario_apertura = st.time_input("Orario apertura")
        restaurants[restaurant_key]["orario_apertura"] = orario_apertura.strftime("%H:%M")
        
        orario_chiusura = st.time_input("Orario chiusura")
        restaurants[restaurant_key]["orario_chiusura"] = orario_chiusura.strftime("%H:%M")
        
        restaurants[restaurant_key]["link"] = st.text_input("Link sito/social")
        restaurants[restaurant_key]["costo"] = st.number_input("Costo (€)", min_value=0.0, step=1.0)
        restaurants[restaurant_key]["prenotazione"] = st.checkbox("Richiede prenotazione")
    
    restaurants[restaurant_key]["note"] = st.text_area("Note", help="Inserisci eventuali note aggiuntive")
    
    return restaurants

def input_shops_section():
    """Gestisce la sezione input per i negozi"""
    st.subheader("🛒 Negozi")
    shops = {}
    shop_key = "negozio_1"
    shops[shop_key] = {}
    
    col1, col2 = st.columns(2)
    
    with col1:
        shops[shop_key]["nome"] = st.text_input("Nome negozio")
        shops[shop_key]["tipo"] = st.selectbox(
            "Tipo negozio", 
            ["Manga", "Cucina", "Cibo", "Elettronica", "Abbigliamento", "Souvenir", "Altro"]
        )
        shops[shop_key]["quartiere"] = st.text_input("Quartiere")
        shops[shop_key]["stazione"] = st.text_input("Stazione più vicina")
    
    with col2:
        orario_apertura = st.time_input("Orario apertura")
        shops[shop_key]["orario_apertura"] = orario_apertura.strftime("%H:%M")
        
        orario_chiusura = st.time_input("Orario chiusura")
        shops[shop_key]["orario_chiusura"] = orario_chiusura.strftime("%H:%M")
        
        shops[shop_key]["link"] = st.text_input("Link sito/social")
        shops[shop_key]["costo"] = st.number_input("Prezzo (€)", min_value=0.0, step=1.0)
    
    shops[shop_key]["note"] = st.text_area("Note", help="Inserisci eventuali note sul budget o sugli acquisti pianificati")
    
    return shops

def input_activities_section():
    """Gestisce la sezione input per le attività"""
    st.subheader("🎯 Attività")
    activities = {}
    activity_key = "attivita_1"
    activities[activity_key] = {}
    
    col1, col2 = st.columns(2)
    
    with col1:
        activities[activity_key]["nome"] = st.text_input("Nome attività")
        activities[activity_key]["tipo"] = st.selectbox(
            "Tipo", 
            ["Museo", "Tempio", "Parco", "Evento", "Tour guidato", "Onsen", "Shopping", "Altro"]
        )
        activities[activity_key]["quartiere"] = st.text_input("Quartiere")
        activities[activity_key]["stazione"] = st.text_input("Stazione più vicina")
    
    with col2:
        orario_apertura = st.time_input("Orario apertura")
        activities[activity_key]["orario_apertura"] = orario_apertura.strftime("%H:%M")
        
        orario_chiusura = st.time_input("Orario chiusura")
        activities[activity_key]["orario_chiusura"] = orario_chiusura.strftime("%H:%M")
        
        activities[activity_key]["link"] = st.text_input("Link sito/social")
        activities[activity_key]["costo"] = st.number_input("Costo (€)", min_value=0.0, step=1.0)
        activities[activity_key]["prenotazione"] = st.checkbox("Richiede prenotazione")
    
    activities[activity_key]["note"] = st.text_area("Note")
    
    return activities

def input_transport_section():
    """Gestisce la sezione input per i trasporti"""
    st.subheader("🚄 Trasporti")
    transports = {}
    use_japan_rail_pass = st.checkbox("Utilizzare Japan Rail Pass")

    if use_japan_rail_pass:
        transports["japan_rail_pass"] = {
            "tipo": "Japan Rail Pass",
            "costo": st.number_input("Costo del Japan Rail Pass (€)", min_value=0.0, step=1.0),
            "durata": st.selectbox("Durata del Pass", ["7 giorni", "14 giorni", "21 giorni"]),
            "note": st.text_area("Note aggiuntive")
        }
    else:
        transport_key = "tratta_1"
        transports[transport_key] = {}
        
        col1, col2 = st.columns(2)
        
        with col1:
            transports[transport_key]["partenza"] = st.text_input("Partenza")
            transports[transport_key]["arrivo"] = st.text_input("Arrivo")
        
        with col2:
            transports[transport_key]["tipo"] = st.selectbox(
                "Tipo di trasporto", 
                ["Shinkansen", "Treno Locale", "Autobus", "Metro", "Taxi", "Altro"]
            )
            transports[transport_key]["costo"] = st.number_input("Costo (€)", min_value=0.0, step=1.0)
        
        transports[transport_key]["note"] = st.text_area("Note")
    
    return transports

def check_and_cleanup_city(city_name, current_data):
    """Verifica se una città ha elementi e la rimuove se è vuota"""
    city_data = current_data["dati_citta"].get(city_name, {})
    has_items = False
    
    for category in ["alloggi", "ristoranti", "negozi", "attivita", "trasporti"]:
        if city_data.get(category) and len(city_data[category]) > 0:
            has_items = True
            break
    
    if not has_items:
        del current_data["dati_citta"][city_name]
    
    return current_data


def display_accommodations(alloggi, city_name):
    """Visualizza i dettagli degli alloggi per una città"""
    if alloggi:
        for key, alloggio in alloggi.items():
            with st.expander(f"🏨 {alloggio.get('nome', 'Alloggio')}", expanded=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Tipo:** {alloggio.get('tipo', 'N/A')}")
                    st.write(f"**Indirizzo:** {alloggio.get('indirizzo', 'N/A')}")
                    st.write(f"**Notti:** {alloggio.get('notti', 0)}")
                    st.write(f"**Costo totale:** €{alloggio.get('costo', 0):,.2f}")
                    st.write(f"**Costo per notte:** €{(alloggio.get('costo', 0) / max(alloggio.get('notti', 1), 1)):,.2f}")
                with col2:
                    st.write(f"**Check-in:** {alloggio.get('check_in_date', 'N/A')}")
                    st.write(f"**Orario check-in:** {alloggio.get('orario_check_in', 'N/A')}")
                    st.write(f"**Check-out:** {alloggio.get('check_out_date', 'N/A')}")
                    st.write(f"**Orario check-out:** {alloggio.get('orario_check_out', 'N/A')}")
                with col3:
                    st.write(f"**Numero conferma:** {alloggio.get('numero_conferma', 'N/A')}")
                    st.write(f"**Codice PIN:** {alloggio.get('codice_pin', 'N/A')}")
                    if alloggio.get('link_booking'):
                        st.write(f"**Link Booking:** [{alloggio['link_booking'].split('/')[-1]}]({alloggio['link_booking']})")
                    if st.button("🗑️", key=f"delete_alloggio_{key}_{city_name}"):
                        current_data = st.session_state.data
                        del current_data["dati_citta"][city_name]["alloggi"][key]
                        current_data = check_and_cleanup_city(city_name, current_data)
                        if db.save_trip_data(current_data):
                            st.rerun()
                
                if alloggio.get('note'):
                    st.write(f"**Note:** {alloggio['note']}")
    else:
        st.info("Nessun alloggio inserito per questa città")

def display_restaurants(ristoranti, city_name):
    """Visualizza i dettagli dei ristoranti per una città"""
    if ristoranti:
        for key, ristorante in ristoranti.items():
            with st.expander(f"🍜 {ristorante.get('nome', 'Ristorante')}", expanded=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Tipo:** {ristorante.get('tipo', 'N/A')}")
                    st.write(f"**Quartiere:** {ristorante.get('quartiere', 'N/A')}")
                    st.write(f"**Stazione:** {ristorante.get('stazione', 'N/A')}")
                with col2:
                    st.write(f"**Orari:** {ristorante.get('orario_apertura', 'N/A')} - {ristorante.get('orario_chiusura', 'N/A')}")
                    st.write(f"**Prenotazione necessaria:** {'Sì' if ristorante.get('prenotazione', False) else 'No'}")
                    st.write(f"**Costo:** €{ristorante.get('costo', 0):,.2f} per persona")
                    if ristorante.get('link'):
                        st.write(f"**Link:** [{ristorante['link'].split('/')[-1]}]({ristorante['link']})")
                with col3:
                    if st.button("🗑️", key=f"delete_ristorante_{key}_{city_name}"):
                        current_data = st.session_state.data
                        del current_data["dati_citta"][city_name]["ristoranti"][key]
                        current_data = check_and_cleanup_city(city_name, current_data)
                        if db.save_trip_data(current_data):
                            st.rerun()
                if ristorante.get('note'):
                    st.write(f"**Note:** {ristorante['note']}")
    else:
        st.info("Nessun ristorante inserito per questa città")

def display_shops(negozi, city_name):
    """Visualizza i dettagli dei negozi per una città"""
    if negozi:
        for key, negozio in negozi.items():
            with st.expander(f"🛍️ {negozio.get('nome', 'Negozio')}", expanded=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Tipo:** {negozio.get('tipo', 'N/A')}")
                    st.write(f"**Quartiere:** {negozio.get('quartiere', 'N/A')}")
                    st.write(f"**Stazione:** {negozio.get('stazione', 'N/A')}")
                with col2:
                    st.write(f"**Orari:** {negozio.get('orario_apertura', 'N/A')} - {negozio.get('orario_chiusura', 'N/A')}")
                    st.write(f"**Prezzo:** €{negozio.get('costo', 0):,.2f}")
                    if negozio.get('link'):
                        st.write(f"**Link:** [{negozio['link'].split('/')[-1]}]({negozio['link']})")
                with col3:
                    if st.button("🗑️", key=f"delete_negozio_{key}_{city_name}"):
                        current_data = st.session_state.data
                        del current_data["dati_citta"][city_name]["negozi"][key]
                        current_data = check_and_cleanup_city(city_name, current_data)
                        if db.save_trip_data(current_data):
                            st.rerun()
                if negozio.get('note'):
                    st.write(f"**Note:** {negozio['note']}")
    else:
        st.info("Nessun negozio inserito per questa città")

def display_activities(attivita, city_name):
    """Visualizza i dettagli delle attività per una città"""
    if attivita:
        for key, attivita_item in attivita.items():
            with st.expander(f"🎯 {attivita_item.get('nome', 'Attività')}", expanded=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Tipo:** {attivita_item.get('tipo', 'N/A')}")
                    st.write(f"**Quartiere:** {attivita_item.get('quartiere', 'N/A')}")
                    st.write(f"**Stazione:** {attivita_item.get('stazione', 'N/A')}")
                with col2:
                    st.write(f"**Orari:** {attivita_item.get('orario_apertura', 'N/A')} - {attivita_item.get('orario_chiusura', 'N/A')}")
                    if attivita_item.get('link'):
                        st.write(f"**Link:** [{attivita_item['link'].split('/')[-1]}]({attivita_item['link']})")
                    st.write(f"**Costo:** €{attivita_item.get('costo', 0):,.2f}")
                    st.write(f"**Prenotazione necessaria:** {'Sì' if attivita_item.get('prenotazione', False) else 'No'}")
                with col3:
                    if st.button("🗑️", key=f"delete_attivita_{key}_{city_name}"):
                        current_data = st.session_state.data
                        del current_data["dati_citta"][city_name]["attivita"][key]
                        current_data = check_and_cleanup_city(city_name, current_data)
                        if db.save_trip_data(current_data):
                            st.rerun()
                if attivita_item.get('note'):
                    st.write(f"**Note:** {attivita_item['note']}")
    else:
        st.info("Nessuna attività inserita per questa città")

def display_transports(trasporti, city_name):
    """Visualizza i dettagli dei trasporti per una città"""
    if trasporti:
        for key, trasporto in trasporti.items():
            if trasporto.get('tipo') == "Japan Rail Pass":
                with st.expander("🎫 Japan Rail Pass", expanded=True):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Costo:** €{trasporto.get('costo', 0):,.2f}")
                        st.write(f"**Durata:** {trasporto.get('durata', 'N/A')}")
                    with col2:
                        st.write(f"**Note:** {trasporto.get('note', 'Nessuna nota')}")
                    with col3:
                        if st.button("🗑️", key=f"delete_jrp_{key}_{city_name}"):
                            current_data = st.session_state.data
                            del current_data["dati_citta"][city_name]["trasporti"][key]
                        if db.save_trip_data(current_data):
                            st.rerun()
            else:
                with st.expander(f"🚄 {trasporto.get('tipo', 'Trasporto')} - {trasporto.get('partenza', 'N/A')} ➔ {trasporto.get('arrivo', 'N/A')}", expanded=True):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Tipo:** {trasporto.get('tipo', 'N/A')}")
                        st.write(f"**Tratta:** {trasporto.get('partenza', 'N/A')} ➔ {trasporto.get('arrivo', 'N/A')}")
                    with col2:
                        st.write(f"**Costo:** €{trasporto.get('costo', 0):,.2f}")
                        st.write(f"**Note:** {trasporto.get('note', 'Nessuna nota')}")
            with col3:
                if st.button("🗑️", key=f"delete_trasporto_{key}_{city_name}"):
                    current_data = st.session_state.data
                    del current_data["dati_citta"][city_name]["trasporti"][key]
                    current_data = check_and_cleanup_city(city_name, current_data)
                    if db.save_trip_data(current_data):
                        st.rerun()
    else:
        st.info("Nessun trasporto inserito per questa città")

def display_city_costs():
    """Visualizza i costi per ogni città"""
    st.header("Riepilogo Finale")
    
    # Filtra solo le città che hanno effettivamente dati
    cities_with_data = []
    for city_name, city_data in st.session_state.data["dati_citta"].items():
        has_items = False
        for category in ["alloggi", "ristoranti", "negozi", "attivita", "trasporti"]:
            if city_data.get(category) and len(city_data[category]) > 0:
                has_items = True
                break
        if has_items:
            cities_with_data.append(city_name)
    
    if cities_with_data:
        selected_city = st.selectbox("Seleziona la città", options=cities_with_data)
        
        if selected_city:
            city_data = st.session_state.data["dati_citta"][selected_city]
            st.subheader(f"Dettaglio costi per {selected_city}")
            
            categoria = st.selectbox(
                "Seleziona categoria",
                ["🏨 Alloggi", "🍜 Ristoranti", "🛍️ Negozi", "🎯 Attività", "🚄 Trasporti"]
            )
            
            st.divider()
            
            if "Alloggi" in categoria:
                display_accommodations(city_data.get("alloggi", {}), selected_city)
            elif "Ristoranti" in categoria:
                display_restaurants(city_data.get("ristoranti", {}), selected_city)
            elif "Negozi" in categoria:
                display_shops(city_data.get("negozi", {}), selected_city)
            elif "Attività" in categoria:
                display_activities(city_data.get("attivita", {}), selected_city)
            elif "Trasporti" in categoria:
                display_transports(city_data.get("trasporti", {}), selected_city)
    else:
        st.warning("Nessuna città con dati disponibili.")

def display_city_summary(city_data):
    """Visualizza il riepilogo dei costi per una città"""
    st.subheader("Riepilogo Costi")
    
    total_costs = {
        "Alloggi": sum(item["costo"] for item in city_data.get("alloggi", {}).values()),
        "Ristoranti": sum(item["costo"] for item in city_data.get("ristoranti", {}).values()),
        "Negozi": sum(item["costo"] for item in city_data.get("negozi", {}).values()),
        "Attività": sum(item["costo"] for item in city_data.get("attivita", {}).values()),
        "Trasporti": sum(item["costo"] for item in city_data.get("trasporti", {}).values())
    }
    
    # Create summary DataFrame
    df_summary = pd.DataFrame(list(total_costs.items()), columns=["Categoria", "Costo"])
    df_summary.loc[len(df_summary)] = ["TOTALE", df_summary["Costo"].sum()]
    
    # Display summary table
    st.dataframe(
        df_summary.style.format({'Costo': '€{:,.2f}'})
                          .set_properties(**{'text-align': 'left'}),
        use_container_width=True
    )

def display_flight_costs():
    """Visualizza i costi di volo e pre-partenza"""
    st.header("Costi Pre-Partenza")
    
    if "costi_partenza" in st.session_state.data:
        pre_partenza = st.session_state.data["costi_partenza"]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            with st.expander("✈️ Dettagli Volo", expanded=True):
                volo = pre_partenza.get('volo', {})
                if volo:
                    st.markdown(f"""
                    **Volo:** {volo.get('partenza', 'N/A')} ➔ {volo.get('arrivo', 'N/A')}  
                    **Data:** {volo.get('data_partenza', 'N/A')}  
                    **Orario:** {volo.get('ora_partenza', 'N/A')}  
                    **Compagnia:** {volo.get('compagnia', 'N/A')}  
                    **Costo Volo:** €{volo.get('costo_base', 0):,.2f}  
                    **Costo Bagagli:** €{volo.get('costo_bagagli', 0):,.2f}  
                    **Totale:** €{volo.get('totale', 0):,.2f}
                    """)
        
        with col2:
            with st.expander("🛡️ Assicurazione", expanded=True):
                assicurazione = pre_partenza.get('assicurazione', {})
                if assicurazione:
                    st.markdown(f"""
                    **Massimale Medico:** €{assicurazione.get('massimale_medico', 0):,.2f}  
                    **Annullamento Volo:** €{assicurazione.get('ritardo_volo', 0):,.2f}  
                    **Bagaglio:** €{assicurazione.get('bagaglio_smarrito', 0):,.2f}  
                    **RC:** €{assicurazione.get('annullamento', 0):,.2f}  
                    **Costo Assicurazione:** €{assicurazione.get('costo', 0):,.2f}  
                    """)
        
        with col3:
            with st.expander("💶 Altro", expanded=True):
                altro = pre_partenza.get('altro', {})
                if altro:
                    st.markdown(f"""
                    **Contanti:** €{altro.get('contanti', 0):,.2f}  
                    **Tasso EUR/JPY:** {altro.get('tasso_cambio', 0):,.2f}  
                    **Yen:** ¥{altro.get('yen', 0):,.0f}  
                    **eSIM:** €{altro.get('costo_sim', 0):,.2f}  
                    **GB inclusi:** {altro.get('gb_sim', 0)}  
                    **Commissioni:** €{altro.get('commissioni', 0):,.2f}  
                    **Totale:** €{altro.get('totale', 0):,.2f}
                    """)
        
        st.metric("💰 Totale Costi Pre-Partenza", f"€{pre_partenza.get('totale_generale', 0):,.2f}")
    else:
        st.info("Nessun dato di pre-partenza disponibile")

def create_japan_map():
    """Crea e restituisce una mappa Folium centrata sul Giappone"""
    mappa = folium.Map(
        location=[36.2048, 138.2529],
        zoom_start=5,
        tiles="cartodb positron",
        control_scale=True
    )
    
    # Aggiungi controlli alla mappa
    mappa.add_child(plugins.MiniMap())
    mappa.add_child(plugins.Fullscreen())
    mappa.add_child(plugins.MeasureControl(
        position='bottomleft',
        primary_length_unit='kilometers'
    ))
    
    # Aggiungi marker per le città con dati attivi
    for city_name, coords in JAPAN_CITIES.items():
        if city_name in st.session_state.data["dati_citta"]:
            # Verifica se ci sono elementi attivi in qualsiasi categoria
            city_data = st.session_state.data["dati_citta"][city_name]
            has_active_items = False
            
            # Controlla tutte le categorie per elementi attivi
            for category in ["alloggi", "ristoranti", "negozi", "attivita", "trasporti"]:
                if city_data.get(category) and len(city_data[category]) > 0:
                    has_active_items = True
                    break
            
            # Aggiungi il marker solo se ci sono elementi attivi
            if has_active_items:
                popup_html = f"""
                <div style='font-family: Arial, sans-serif; width: 200px;'>
                    <h4>{city_name}</h4>
                    <p>Clicca per visualizzare i dettagli</p>
                </div>
                """
                
                folium.Marker(
                    location=[coords['lat'], coords['lon']],
                    popup=folium.Popup(popup_html, max_width=300),
                    tooltip=f"{city_name}",
                    icon=folium.Icon(color='red', icon='info-sign')
                ).add_to(mappa)
    
    return mappa

def handle_pre_partenza():
    """Gestisce la sezione pre-partenza"""
    st.title("Inserisci Costi Pre-Partenza")
    
    # Carica i dati esistenti
    existing_data = st.session_state.data.get("costi_partenza", {})
    
    # Pulsante per pulire i dati
    if st.button("🧹 Pulisci Contenuto", type="secondary"):
        st.session_state.data["costi_partenza"] = {}
        st.experimental_rerun()
    
    with st.form("costi_partenza"):
        st.subheader("✈️ Dettagli Volo")
        col1, col2 = st.columns(2)
        with col1:
            volo_data = existing_data.get("volo", {})
            partenza = st.text_input("Volo da (Città di Partenza)", 
                                   value=volo_data.get("partenza", ""))
            arrivo = st.text_input("Volo a (Città di Arrivo)", 
                                 value=volo_data.get("arrivo", ""))
            durata = st.text_input("Durata del Volo (es. 12 ore)", 
                                 value=volo_data.get("durata", ""))
            fuso_orario = st.text_input("Fuso Orario (es. GMT+9)", 
                                      value=volo_data.get("fuso_orario", ""))
        
        with col2:
            data_partenza = st.date_input("Data di Partenza", 
                value=datetime.strptime(volo_data.get("data_partenza", datetime.now().strftime("%Y-%m-%d")), "%Y-%m-%d"))
            ora_partenza = st.time_input("Orario di Partenza", 
                value=datetime.strptime(volo_data.get("ora_partenza", "00:00"), "%H:%M").time())
            data_ritorno = st.date_input("Data di Ritorno", 
                value=datetime.strptime(volo_data.get("data_ritorno", datetime.now().strftime("%Y-%m-%d")), "%Y-%m-%d"))
            ora_ritorno = st.time_input("Orario di Ritorno", 
                value=datetime.strptime(volo_data.get("ora_ritorno", "00:00"), "%H:%M").time())
        
        st.divider()

        col3, col4 = st.columns(2)
        with col3:
            volo = st.number_input("Costo del volo (€)", 
                                 value=volo_data.get("costo_base", 0.0), 
                                 min_value=0.0, step=10.0)
            compagnia = st.text_input("Compagnia Aerea", 
                                    value=volo_data.get("compagnia", ""))
        with col4:
            scali = st.number_input("Numero di scali", 
                                  value=volo_data.get("scali", 0), 
                                  min_value=0, step=1)
            bagagli = st.number_input("Costo bagagli (€)", 
                                    value=volo_data.get("costo_bagagli", 0.0), 
                                    min_value=0.0, step=10.0)

        st.divider()
        
        st.subheader("🛡️ Assicurazione e Costi Associati")
        col5, col6 = st.columns(2)
        assicurazione_data = existing_data.get("assicurazione", {})
        with col5:
            massimale_medico = st.number_input("Massimale medico (€)", 
                value=assicurazione_data.get("massimale_medico", 0.0), min_value=0.0, step=1000.0)
            ritardo_volo = st.number_input("Copertura annullamento volo (€)", 
                value=assicurazione_data.get("ritardo_volo", 0.0), min_value=0.0, step=100.0)
            bagaglio_smarrito = st.number_input("Copertura bagaglio (€)",
                value=assicurazione_data.get("bagaglio_smarrito", 0.0), min_value=0.0, step=10.0)
        with col6: 
            annullamento = st.number_input("Copertura responsabilità civile (€)", 
                value=assicurazione_data.get("annullamento", 0.0), min_value=0.0, step=100.0)
            costo_assicurazione = st.number_input("Costo assicurazione (€)", 
                value=assicurazione_data.get("costo", 0.0), min_value=0.0, step=10.0)

        
        st.subheader("💶 Altro")
        col7, col8 = st.columns(2)
        altro_data = existing_data.get("altro", {})
        with col7:
            sim = st.number_input("Costo eSIM (€)", 
                value=altro_data.get("costo_sim", 0.0), min_value=0.0, step=10.0)
            sim_gb = st.number_input("GB inclusi", 
                value=altro_data.get("gb_sim", 0), min_value=0, step=1)
        with col8:
            contanti = st.number_input("Contanti da ritirare (€)", 
                value=altro_data.get("contanti", 0.0), min_value=0.0, step=100.0)
            tasso_cambio = st.number_input("Tasso di cambio EUR/JPY", 
                value=altro_data.get("tasso_cambio", 160.0), min_value=0.0, step=0.1)

        commissioni = st.number_input("Commissioni cambio (€)", 
            value=altro_data.get("commissioni", 0.0), min_value=0.0, step=0.1)

        submit = st.form_submit_button("Salva Costi Pre-Partenza")
        
        if submit:
            total_flight = volo + bagagli
            total_insurance = costo_assicurazione
            total_altri_costi = sim
            
            pre_partenza_data = {
                "volo": {
                    "partenza": partenza,
                    "arrivo": arrivo,
                    "durata": durata,
                    "fuso_orario": fuso_orario,
                    "data_partenza": data_partenza.strftime("%Y-%m-%d"),
                    "ora_partenza": ora_partenza.strftime("%H:%M"),
                    "data_ritorno": data_ritorno.strftime("%Y-%m-%d"),
                    "ora_ritorno": ora_ritorno.strftime("%H:%M"),
                    "costo_base": volo,
                    "compagnia": compagnia,
                    "scali": scali,
                    "costo_bagagli": bagagli,
                    "totale": total_flight
                },
                "assicurazione": {
                    "massimale_medico": massimale_medico,
                    "ritardo_volo": ritardo_volo,
                    "bagaglio_smarrito": bagaglio_smarrito,
                    "annullamento": annullamento,
                    "costo": total_insurance
                },
                "altro": {
                    "costo_sim": sim,
                    "gb_sim": sim_gb,
                    "contanti": contanti,
                    "tasso_cambio": tasso_cambio,
                    "commissioni": commissioni,
                    "yen": contanti * tasso_cambio,
                    "totale": total_altri_costi
                },
                "totale_generale": total_flight + total_insurance + total_altri_costi
            }
            
            st.session_state.data["costi_partenza"] = pre_partenza_data
            if db.save_trip_data(st.session_state.data):
                st.success("Dati salvati con successo!")

def handle_city_activities():
    """Gestisce la sezione attività per città"""
    st.title("Inserisci Dati per Città")
    
    # Verifica che le città siano disponibili
    available_cities = list(JAPAN_CITIES.keys())
    if not available_cities:
        st.error("Nessuna città disponibile nel database")
        return
        
    # Selezione della città
    citta = st.selectbox("Seleziona la città", options=available_cities)
    
    try:
        # Inizializza il dizionario delle città se non esiste
        if "dati_citta" not in st.session_state.data:
            st.session_state.data["dati_citta"] = {}
        
        # Inizializza la struttura dati per la città selezionata se non esiste
        if citta not in st.session_state.data["dati_citta"]:
            empty_structure = db.get_empty_city_structure()
            # Aggiungi le coordinate dalla costante JAPAN_CITIES
            if citta in JAPAN_CITIES:
                empty_structure["coordinate"] = JAPAN_CITIES[citta]
            st.session_state.data["dati_citta"][citta] = empty_structure
            
            # Salva immediatamente la struttura vuota nel database
            if not db.save_trip_data(st.session_state.data):
                st.error(f"Errore durante l'inizializzazione dei dati per {citta}")
                return
    except Exception as e:
        st.error(f"Errore durante l'elaborazione dei dati: {str(e)}")
        return
        
    # Applica stili per i pulsanti
    st.markdown("""
        <style>
        div[data-baseweb="select"] > div {
            background-color: white;
            border-radius: 4px;
            margin-bottom: 20px;
        }
        
        .stButton > button {
            width: 100%;
            border: 2px solid transparent !important;
            background-color: white !important;
            color: #0E1117 !important;
            font-weight: 500 !important;
            padding: 15px 25px !important;
            margin: 4px 2px !important;
            border-radius: 4px !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
            transition: all 0.3s ease !important;
        }
        
        .stButton > button:hover {
            box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
            border-color: #ddd !important;
        }
        
        .stButton > button[kind="primary"] {
            border-color: #FF4B4B !important;
            font-weight: 600 !important;
        }
        
        .activity-section {
            margin-top: 2rem;
            padding: 20px;
            border-radius: 4px;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        </style>
    """, unsafe_allow_html=True)

    # Layout dei pulsanti
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        alloggi_active = st.button(
            "🏨 Alloggi",
            key="btn_alloggi",
            use_container_width=True,
            type="primary" if "selected_activity" not in st.session_state or st.session_state.selected_activity == "alloggi" else "secondary"
        )
    with col2:
        ristoranti_active = st.button(
            "🍜 Ristoranti",
            key="btn_ristoranti",
            use_container_width=True,
            type="primary" if "selected_activity" in st.session_state and st.session_state.selected_activity == "ristoranti" else "secondary"
        )
    with col3:
        negozi_active = st.button(
            "🛍️ Negozi",
            key="btn_negozi",
            use_container_width=True,
            type="primary" if "selected_activity" in st.session_state and st.session_state.selected_activity == "negozi" else "secondary"
        )
    with col4:
        attivita_active = st.button(
            "🎯 Attività",
            key="btn_attivita",
            use_container_width=True,
            type="primary" if "selected_activity" in st.session_state and st.session_state.selected_activity == "attivita" else "secondary"
        )
    with col5:
        trasporti_active = st.button(
            "🚄 Trasporti",
            key="btn_trasporti",
            use_container_width=True,
            type="primary" if "selected_activity" in st.session_state and st.session_state.selected_activity == "trasporti" else "secondary"
        )

    # Gestione della selezione
    if alloggi_active:
        st.session_state.selected_activity = "alloggi"
    elif ristoranti_active:
        st.session_state.selected_activity = "ristoranti"
    elif negozi_active:
        st.session_state.selected_activity = "negozi"
    elif attivita_active:
        st.session_state.selected_activity = "attivita"
    elif trasporti_active:
        st.session_state.selected_activity = "trasporti"

    # Mostra la sezione selezionata
    if "selected_activity" not in st.session_state:
        st.session_state.selected_activity = "alloggi"

    st.divider()
    
    with st.form("city_data_form"):
        if st.session_state.selected_activity == "alloggi":
            new_alloggi = input_accommodation_section()
            data_to_save = {"alloggi": new_alloggi}
        elif st.session_state.selected_activity == "ristoranti":
            new_ristoranti = input_restaurants_section()
            data_to_save = {"ristoranti": new_ristoranti}
        elif st.session_state.selected_activity == "negozi":
            new_negozi = input_shops_section()
            data_to_save = {"negozi": new_negozi}
        elif st.session_state.selected_activity == "attivita":
            new_attivita = input_activities_section()
            data_to_save = {"attivita": new_attivita}
        elif st.session_state.selected_activity == "trasporti":
            new_trasporti = input_transport_section()
            data_to_save = {"trasporti": new_trasporti}
        
        submit = st.form_submit_button("Salva Dati")
        
        if submit:
            if citta not in st.session_state.data["dati_citta"]:
                st.session_state.data["dati_citta"][citta] = db.get_empty_city_structure()
            
            for category, data in data_to_save.items():
                if data:  # se ci sono dati da salvare
                    # Ottieni il numero massimo esistente per la categoria
                    existing_items = st.session_state.data["dati_citta"][citta][category]
                    existing_keys = [k for k in existing_items.keys() if k.startswith(f"{category[:-1]}_")]
                    max_num = 0
                    if existing_keys:
                        max_num = max([int(k.split('_')[-1]) for k in existing_keys])
                    
                    # Aggiungi i nuovi elementi con numeri incrementali
                    for item in data.values():
                        if isinstance(item, dict) and (item.get('nome') or category == "trasporti"):
                            max_num += 1
                            new_key = f"{category[:-1]}_{max_num}"
                            st.session_state.data["dati_citta"][citta][category][new_key] = item
            
            if db.save_trip_data(st.session_state.data):
                st.success(f"Dati salvati con successo per {citta}!")
                st.rerun()  # Aggiorna la pagina per mostrare i nuovi dati
                
def handle_costs_summary():
    """Gestisce la sezione riepilogo"""
    st.title("Riepilogo")
    
    # Ottieni i dati aggiornati dal database
    current_data = db.get_trip_data()
    st.session_state.data = current_data
    
    tab_selezionata = st.radio(
        "Seleziona una sezione",
        ("Costi Pre-Partenza", "Riepilogo Finale"),
        horizontal=True
    )
    
    if tab_selezionata == "Costi Pre-Partenza":
        display_flight_costs()
    elif tab_selezionata == "Riepilogo Finale":
        display_city_costs()

def display_photo_gallery():
    """Mostra la galleria fotografica con link personalizzabile e salvataggio nel database"""
    st.title("Galleria Fotografica 📸")
    
    # Recupera il link personalizzato dal database
    if "custom_gallery_link" not in st.session_state.data:
        st.session_state.data["custom_gallery_link"] = ""
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("""
        ### 🖼️ Sfoglia le foto del viaggio
        """)
        
        # Form per il link personalizzato
        with st.form("gallery_link_form"):
            custom_link = st.text_input(
                "Inserisci un link personalizzato alla galleria (es. OneDrive, Dropbox, etc.)",
                value=st.session_state.data["custom_gallery_link"],
                key="gallery_link_input"
            )
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                submit_link = st.form_submit_button("💾 Salva Link")
            with col_btn2:
                if custom_link:
                    st.markdown(f'<a href="{custom_link}" target="_blank" class="css-1cpxqw2 edgvbvh9"><span class="css-tkw1gz edgvbvh8">🔗 Apri Link</span></a>', unsafe_allow_html=True)
            
            if submit_link and custom_link:
                st.session_state.data["custom_gallery_link"] = custom_link
                if db.save_trip_data(st.session_state.data):
                    st.success("Link salvato con successo!")
                else:
                    st.error("Errore nel salvataggio del link")
def main():
    """Funzione principale dell'applicazione"""
    st.sidebar.title("Viaggio in Giappone")
    pagina = st.sidebar.selectbox(
        "Seleziona una pagina",
        ["Home", "Volo e Assicurazione", "Attività per Città", "Riepilogo Finale", "Galleria Foto"]
    )
    
    if pagina == "Home":
        st.title("Pianificazione Viaggio in Giappone 🗾")
        
        # Mostra la mappa
        mappa = create_japan_map()
        st_folium(mappa, width=800, height=600)
        
        # Mostra statistiche generali se ci sono dati
        if st.session_state.data["dati_citta"]:
            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
            st.subheader("Statistiche Generali")
            col1, col2, col3 = st.columns(3)
            
            # Calcola il numero di città con elementi attivi
            active_cities = 0
            total_cost = 0
            for city_name, city_data in st.session_state.data["dati_citta"].items():
                has_active_items = False
                city_cost = 0
                for category in ["alloggi", "ristoranti", "negozi", "attivita", "trasporti"]:
                    if city_data.get(category) and len(city_data[category]) > 0:
                        has_active_items = True
                        if category in ["alloggi", "attivita", "trasporti"]:
                            city_cost += sum(item.get("costo", 0) for item in city_data[category].values())
                
                if has_active_items:
                    active_cities += 1
                    total_cost += city_cost
            
            pre_departure_cost = st.session_state.data.get("costi_partenza", {}).get("totale_generale", 0)
            
            with col1:
                st.metric("Città Pianificate", active_cities)
            with col2:
                st.metric("Costi Pre-Partenza", f"€{pre_departure_cost:,.2f}")
        
        else:
            st.info("Nessun dato inserito. Inizia aggiungendo i costi pre-partenza o le attività per città!")
            
    elif pagina == "Volo e Assicurazione":
        handle_pre_partenza()
        
    elif pagina == "Attività per Città":
        handle_city_activities()
        
    elif pagina == "Riepilogo Finale":
        handle_costs_summary()
        
    elif pagina == "Galleria Foto":
        display_photo_gallery()


if __name__ == "__main__":
    if 'data' not in st.session_state:
            st.session_state.data = db.get_trip_data()
    main()