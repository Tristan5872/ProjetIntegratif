import paho.mqtt.client as mqtt
import ssl
import json
import os
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from dotenv import load_dotenv

# Charger les variables depuis le fichier .env
load_dotenv()

# --- CONFIG INFLUXDB ---
influx_url = os.getenv("INFLUX_URL")
influx_token = os.getenv("INFLUX_TOKEN")
influx_org = os.getenv("INFLUX_ORG")
influx_bucket = os.getenv("INFLUX_BUCKET")

client_influx = InfluxDBClient(url=influx_url, token=influx_token, org=influx_org)
write_api = client_influx.write_api()

# === Callback quand un message arrive ===
def on_message(client, userdata, msg):
    print("📡 Message reçu sur :", msg.topic)
    payload = msg.payload.decode()

    try:
        data = json.loads(payload)
        device_id = data["end_device_ids"]["device_id"]
        values = data["uplink_message"]["decoded_payload"]

        print(f"📦 Données du device {device_id} : {values}")

        point = Point("mesures_serre") \
            .tag("device", device_id) \
            .time(datetime.utcnow(), WritePrecision.NS)

        for key in ["temperature", "humidity", "light", "co2", "motion", "vdd"]:
            if key in values:
                point.field(key, float(values[key]))

        write_api.write(bucket=influx_bucket, org=influx_org, record=point)
        print("✅ Données enregistrées dans InfluxDB")

    except Exception as e:
        print("⚠️ Erreur lors du traitement :", e)

# --- CONFIG MQTT ---
mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(
    os.getenv("MQTT_USERNAME"),
    password=os.getenv("MQTT_PASSWORD")
)

mqtt_client.tls_set(ca_certs="/etc/ssl/certs/ca-certificates.crt", cert_reqs=ssl.CERT_REQUIRED)
mqtt_client.connect(os.getenv("MQTT_BROKER"), port=int(os.getenv("MQTT_PORT")))

# 🔔 Abonnement à plusieurs capteurs
mqtt_client.subscribe("v3/rt-ttn-app@ttn/devices/ers2-02/up")
mqtt_client.subscribe("v3/rt-ttn-app@ttn/devices/ers2-co2-01/up")

mqtt_client.on_message = on_message

print("🔁 En écoute sur les topics...")
mqtt_client.loop_forever()
