from flask import Flask, render_template, request, jsonify
from ia import *
import json
import os
import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient
from dotenv import load_dotenv

load_dotenv()

influx_url = os.getenv("INFLUX_URL")
influx_token = os.getenv("INFLUX_TOKEN")
influx_org = os.getenv("INFLUX_ORG")
influx_bucket = os.getenv("INFLUX_BUCKET")

client_influx = InfluxDBClient(url=influx_url, token=influx_token, org=influx_org)
query_api = client_influx.query_api()

def get_last_data():
    query = f'''
    from(bucket:"{influx_bucket}")
        |> range(start: -1h)
        |> filter(fn: (r) => r._measurement == "mesures_serre")
        |> filter(fn: (r) => r["device"] == "ers-02" or r["device"] == "ers-co2-01")
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

            if device == "ers-02":
                data["interieur"][field] = value
            elif device == "ers-co2-01":
                data["exterieur"][field] = value

    return data

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/historique')
def historique():
    return render_template('historique.html')

@app.route('/meteo')
def meteo():
    return render_template('meteo.html')

# === Route Flask pour activer le chauffage (TOR1 ON via MQTT + TTN) ===
@app.route('/chauffage_on')
def chauffage_on():
    mqtt_client = mqtt.Client()
    mqtt_client.username_pw_set(os.getenv("MQTT_USERNAME"), os.getenv("MQTT_PASSWORD"))
    mqtt_client.tls_set(ca_certs="/etc/ssl/certs/ca-certificates.crt")
    mqtt_client.connect(os.getenv("MQTT_BROKER"), int(os.getenv("MQTT_PORT")))

    downlink_topic = "v3/rt-ttn-app@ttn/devices/adeunis-dry-01/down/push"
    payload = {
        "downlinks": [{
            "frm_payload": "0601010000",  # TOR1 ON (chauffage)
            "f_port": 1,
            "priority": "NORMAL"
        }]
    }

    mqtt_client.publish(downlink_topic, json.dumps(payload))
    return "Commande chauffage envoyée."

# Partie IA
@app.route('/ai_analysis', methods=['POST'])
def call_ai():
    data = request.get_json()
    meteo = data.get("meteo", "")
    recommendation = analyse_meteo(meteo)
    return jsonify({"recommendation": recommendation})

# Partie récupération des données sur la BDD 
@app.route('/api/serre')
def api_serre():
    data = get_last_data()
    return jsonify(data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
