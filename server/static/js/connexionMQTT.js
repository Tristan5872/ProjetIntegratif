const options = {
    username: 'mqtt-access@ttn',
    password: 'NNSXS.LJDO5CK3GZ6ORBP6RQ3DDQBIDUXOA73RSEUEB5Y.7N6NA427MLRFJEGKV62WMNTLB3R6L6BDNUBHDQVDEX6PMGXTKXHQ',
    protocol: 'wss'
};

const client = mqtt.connect('wss://eu1.cloud.thethings.network/mqtt', options);

client.on('connect', () => {
    console.log("Connecté à TTN MQTT");
    client.subscribe('v3/tonAppID@ttn/devices/+/up');
});

client.on('message', (topic, message) => {
    const json = JSON.parse(message.toString());
    const payload = json.uplink_message.decoded_payload;

    document.getElementById('temperature').textContent = payload.temperature;
    document.getElementById('humidity').textContent = payload.humidity;
});