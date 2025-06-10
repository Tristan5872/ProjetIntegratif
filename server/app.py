from flask import Flask, render_template, request, jsonify
from ia import *  # Import des fonctions d'analyse IA (ex: analyse_meteo, analyse_sante)
import paho.mqtt.client as mqtt
import json
import os
from influxdb_client import InfluxDBClient
from dotenv import load_dotenv
import base64
import requests

# Chargement des variables d'environnement depuis un fichier .env
load_dotenv()

# Récupération des variables d'environnement pour InfluxDB
influx_url = os.getenv("INFLUX_URL")
influx_token = os.getenv("INFLUX_TOKEN")
influx_org = os.getenv("INFLUX_ORG")
influx_bucket = os.getenv("INFLUX_BUCKET")

# Initialisation du client InfluxDB
client_influx = InfluxDBClient(url=influx_url, token=influx_token, org=influx_org)
query_api = client_influx.query_api()

# Fonction pour récupérer les dernières données des capteurs
def get_last_data():
    query = f'''
    from(bucket:"{influx_bucket}")
        |> range(start: -1h)
        |> filter(fn: (r) => r._measurement == "mesures_serre")
        |> filter(fn: (r) => r["device"] == "ers2-02" or r["device"] == "ers2-co2-01")
        |> last()
    '''
    tables = query_api.query(query)
    data = {
        "interieur": {},
        "exterieur": {}
    }
    for table in tables:
        for record in table.records:
            device = record.values.get("device")
            field = record.get_field()
            value = record.get_value()
            if device == "ers2-02":
                data["exterieur"][field] = value
            elif device == "ers2-co2-01":
                data["interieur"][field] = value
    return data

app = Flask(__name__)
etat_chauffage = False

@app.route('/')
def home():
    global etat_chauffage
    data = get_last_data()
    bg_color = "rgb(98, 158, 238)" if etat_chauffage else "rgb(250, 88, 43)"
    btn_text = "Éteindre le chauffage" if etat_chauffage else "Allumer le chauffage"
    return render_template('index.html', etat_chauffage=etat_chauffage, bg_color=bg_color, btn_text=btn_text, data=data)

@app.route('/historique')
def historique():
    return render_template('historique.html')

@app.route('/meteo')
def meteo():
    return render_template('meteo.html')

@app.route('/notification')
def notification():
    return render_template('notification.html')

@app.route('/toggle_chauffage')
def toggle_chauffage():
    global etat_chauffage
    mqtt_client = mqtt.Client()
    def on_publish(client, userdata, mid):
        print(f"[INFO] Message MQTT publié avec succès, mid={mid}")
    mqtt_client.on_publish = on_publish
    mqtt_client.username_pw_set(os.getenv("MQTT_USERNAME"), os.getenv("MQTT_PASSWORD"))
    mqtt_client.tls_set(ca_certs="/etc/ssl/certs/ca-certificates.crt")
    mqtt_client.connect(os.getenv("MQTT_BROKER"), int(os.getenv("MQTT_PORT")))
    downlink_topic = "v3/rt-ttn-app@ttn/devices/adeunis-dry-01/down/push"
    if etat_chauffage:
        payload_hex = "060100000002"
        etat_chauffage = False
    else:
        payload_hex = "060100000001"
        etat_chauffage = True
    raw_bytes = bytes.fromhex(payload_hex)
    payload_b64 = base64.b64encode(raw_bytes).decode()
    payload = {
        "downlinks": [{
            "frm_payload": payload_b64,
            "f_port": 1,
            "priority": "NORMAL"
        }]
    }
    result, mid = mqtt_client.publish(downlink_topic, json.dumps(payload))
    if result == mqtt.MQTT_ERR_SUCCESS:
        print("[INFO] La publication MQTT a été acceptée localement.")
    else:
        print("[ERROR] Échec de la publication MQTT.")
    data = get_last_data()
    bg_color = "rgb(98, 158, 238)" if etat_chauffage else "rgb(250, 88, 43)"
    btn_text = "Éteindre le chauffage" if etat_chauffage else "Allumer le chauffage"
    return render_template("index.html", etat_chauffage=etat_chauffage, bg_color=bg_color, btn_text=btn_text, data=data)

@app.route('/ai_analysis', methods=['POST'])
def call_ai():
    data = request.get_json()
    meteo = data.get("meteo", "")
    recommendation = analyse_meteo(meteo)
    return jsonify({"recommendation": recommendation})

@app.route('/analyse_sante', methods=['POST'])
def analyse_sante_plantes():
    data = request.get_json()
    temperature_int = data.get("temperature_int", "")
    humidite_int = data.get("humidite_int", "")
    co2_int = data.get("co2_int", "")
    lumiere_int = data.get("lumiere_int", "")
    temperature_ext = data.get("temperature_ext", "")
    humidite_ext = data.get("humidite_ext", "")
    lumiere_ext = data.get("lumiere_ext", "")

    donnees = {
        "interieur": {
            "temperature": temperature_int,
            "humidity": humidite_int,
            "co2": co2_int,
            "light": lumiere_int
        },
        "exterieur": {
            "temperature": temperature_ext,
            "humidity": humidite_ext,
            "light": lumiere_ext
        }
    }

    recommendation = analyse_sante(donnees)
    return jsonify({"recommendation": recommendation})


@app.route('/api/serre')
def api_serre():
    data = get_last_data()
    return jsonify(data)

@app.route('/historique_data/<periode>')
def historique_data_par_periode(periode):
    if periode == 'ajd':
        start = "-1d"
    elif periode == 'semaine':
        start = "-7d"
    elif periode == 'mois':
        start = "-30d"
    elif periode == 'sixmois':
        start = "-180d"
    elif periode == 'an':
        start = "-365d"
    else:
        return jsonify([])

    query = f'''
    from(bucket: "{influx_bucket}")
      |> range(start: {start})
      |> filter(fn: (r) => r._measurement == "actions")
      |> filter(fn: (r) => r._field == "action")
      |> sort(columns: ["_time"], desc: true)
    '''

    try:
        tables = query_api.query(query)
        result = []
        for table in tables:
            for record in table.records:
                result.append({
                    "date": record.get_time().strftime("%Y-%m-%d %H:%M:%S"),
                    "action": record.get_value()
                })
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ⚠️ Toujours à la toute fin :
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
