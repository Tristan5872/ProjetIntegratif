const mqtt=require('mqtt')
const options = {
    clientID: 'groupe3projetint',
    username: 'rt-ttn-app@ttn',
    password: 'NNSXS.TOR3G445SGXWD56HWGCKVUTFVXZMREAHKCVIFNA.FOSLC4TQYFZA6J6YBAOSDGJXXN543OGRF7Z5GVYUHDGOSZUMUBAQ',
};

const client = mqtt.connect('mqtts://eu1.cloud.thethings.network:8883', options);

client.on('connect', () => {
    console.log("Connecté à TTN MQTT");
    client.subscribe('v3/rt-ttn-app@ttn/devices/+/up');
});

client.on('message', (topic, message) => {
    const json = JSON.parse(message.toString());
    const payload = json.uplink_message.decoded_payload;

    document.getElementById('temperature').textContent = payload.temperature;
    document.getElementById('humidity').textContent = payload.humidity;
});