from flask import Flask, render_template, request, jsonify
from ia import *  # Import des fonctions d'analyse IA (ex: analyse_meteo)
import paho.mqtt.client as mqtt
import json
import os
from influxdb_client import InfluxDBClient
from dotenv import load_dotenv
import base64

# Chargement des variables d'environnement depuis un fichier .env
load_dotenv()

# Récupération des variables d'environnement pour InfluxDB
influx_url = os.getenv("INFLUX_URL")
influx_token = os.getenv("INFLUX_TOKEN")
influx_org = os.getenv("INFLUX_ORG")
influx_bucket = os.getenv("INFLUX_BUCKET")

# Initialisation du client InfluxDB avec URL, token et organisation
client_influx = InfluxDBClient(url=influx_url, token=influx_token, org=influx_org)
query_api = client_influx.query_api()

# Fonction pour récupérer les dernières données des capteurs depuis InfluxDB
def get_last_data():
    # Requête Flux pour récupérer les dernières mesures dans les dernières 1h
    query = f'''
    from(bucket:"{influx_bucket}")
        |> range(start: -1h)
        |> filter(fn: (r) => r._measurement == "mesures_serre")
        |> filter(fn: (r) => r["device"] == "ers2-02" or r["device"] == "ers2-co2-01")
        |> last()
    '''

    # Exécution de la requête InfluxDB
    tables = query_api.query(query)

    # Structure de données pour stocker les résultats par zone
    data = {
        "interieur": {},
        "exterieur": {}
    }

    # Parcours des tables retournées (une table par série de données)
    for table in tables:
        for record in table.records:
            device = record.values.get("device")  # Récupération du nom du device
            field = record.get_field()             # Nom du champ (ex: temperature, co2)
            value = record.get_value()             # Valeur mesurée

            # Selon le device, on stocke les données dans la bonne zone
            if device == "ers2-02":
                data["exterieur"][field] = value
            elif device == "ers2-co2-01":
                data["interieur"][field] = value

    return data


# Création de l'application Flask
app = Flask(__name__)

# Variable globale pour mémoriser l'état du chauffage (False = éteint, True = allumé)
etat_chauffage = False


# Route principale affichant la page d'accueil (tableau de bord)
@app.route('/')
def home():
    global etat_chauffage

    # Récupération des dernières données capteurs
    data = get_last_data()

    # Détermination des couleurs et texte du bouton selon état chauffage
    bg_color = "rgb(98, 158, 238)" if etat_chauffage else "rgb(250, 88, 43)"
    btn_text = "Éteindre le chauffage" if etat_chauffage else "Allumer le chauffage"

    # Rend le template index.html en lui passant les variables
    return render_template('index.html', etat_chauffage=etat_chauffage, bg_color=bg_color, btn_text=btn_text, data=data)


# Route affichant la page historique
@app.route('/historique')
def historique():
    return render_template('historique.html')


# Route affichant la page météo
@app.route('/meteo')
def meteo():
    return render_template('meteo.html')


# Route pour activer/désactiver le chauffage via MQTT et mise à jour de l'état
@app.route('/toggle_chauffage')
def toggle_chauffage():
    global etat_chauffage

    # Création et configuration client MQTT
    mqtt_client = mqtt.Client()

    # Callback pour confirmer la publication
    def on_publish(client, userdata, mid):
        print(f"[INFO] Message MQTT publié avec succès, mid={mid}")

    mqtt_client.on_publish = on_publish

    mqtt_client.username_pw_set(os.getenv("MQTT_USERNAME"), os.getenv("MQTT_PASSWORD"))
    mqtt_client.tls_set(ca_certs="/etc/ssl/certs/ca-certificates.crt")
    mqtt_client.connect(os.getenv("MQTT_BROKER"), int(os.getenv("MQTT_PORT")))

    # Topic MQTT pour envoyer la commande à l'appareil TTN
    downlink_topic = "v3/rt-ttn-app@ttn/devices/adeunis-dry-01/down/push"

    # Préparation du payload en hexadécimal selon l'état souhaité
    if etat_chauffage:
        payload_hex = "0601000000"  # Commande OFF chauffage
        etat_chauffage = False
    else:
        payload_hex = "0601010000"  # Commande ON chauffage
        etat_chauffage = True

    # Conversion du payload hex en base64 pour le format attendu par TTN
    raw_bytes = bytes.fromhex(payload_hex)
    payload_b64 = base64.b64encode(raw_bytes).decode()

    # Création du message JSON à publier sur MQTT
    payload = {
        "downlinks": [{
            "frm_payload": payload_b64,
            "f_port": 1,
            "priority": "NORMAL"
        }]
    }

    # Publication du message sur le topic MQTT
    result, mid = mqtt_client.publish(downlink_topic, json.dumps(payload))

    # Vérification du résultat immédiat
    if result == mqtt.MQTT_ERR_SUCCESS:
        print("[INFO] La publication MQTT a été acceptée localement.")
        publication_ok = True
    else:
        print("[ERROR] Échec de la publication MQTT.")
        publication_ok = False

    # On continue avec le rechargement de la page
    data = get_last_data()
    bg_color = "rgb(98, 158, 238)" if etat_chauffage else "rgb(250, 88, 43)"
    btn_text = "Éteindre le chauffage" if etat_chauffage else "Allumer le chauffage"

    # Pour test : on pourrait aussi passer publication_ok au template si tu veux l'afficher dans la page
    return render_template("index.html", etat_chauffage=etat_chauffage, bg_color=bg_color, btn_text=btn_text, data=data)


# Route API POST pour analyser les données météo avec l'IA
@app.route('/ai_analysis', methods=['POST'])
def call_ai():
    # Récupère les données JSON envoyées en POST
    data = request.get_json()
    meteo = data.get("meteo", "")  # Extraction du texte météo

    # Appel de la fonction d'analyse IA (externe dans ia.py)
    recommendation = analyse_meteo(meteo)

    # Retourne la recommandation au format JSON
    return jsonify({"recommendation": recommendation})


# Route API GET pour récupérer les dernières données de la serre au format JSON
@app.route('/api/serre')
def api_serre():
    data = get_last_data()
    return jsonify(data)


# Point d'entrée principal de l'application Flask
if __name__ == '__main__':
    # Lancement du serveur Flask accessible sur toutes les interfaces réseau
    # sur le port 80 (HTTP)
    app.run(host='0.0.0.0', port=80)
